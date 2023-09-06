# -*- coding: utf-8 -*-
"""
****************************************************
*          Basic Language Model Backend            *
*            (c) 2023 Alexander Hering             *
****************************************************
"""
import os
from uuid import UUID
from time import sleep
from datetime import datetime as dt
from typing import Optional, Any, List
from src.configuration import configuration as cfg
from src.utility.gold.filter_mask import FilterMask
from src.utility.bronze import sqlalchemy_utility
from src.model.backend_control.data_model import populate_data_instrastructure
from src.model.backend_control.llm_pool import ThreadedLLMPool


class BackendController(object):
    """
    Controller class for handling backend interface requests.
    """

    def __init__(self, working_directory: str = None, database_uri: str = None) -> None:
        """
        Initiation method.
        :param working_directory: Working directory.
            Defaults to folder 'processes' folder under standard backend data path.
        :param database_uri: Database URI.
            Defaults to 'backend.db' file under default data path.
        """
        self.working_directory = cfg.PATHS.BACKEND_PATH if working_directory is None else working_directory
        if not os.path.exists(self.working_directory):
            os.makedirs(self.working_directory)

        self._logger = cfg.LOGGER
        self._logger.info("Automapping existing structures")
        self.base = sqlalchemy_utility.automap_base()
        self.engine = sqlalchemy_utility.get_engine(
            f"sqlite:///{os.path.join(cfg.PATHS.DATA_PATH, 'backend.db')}" if database_uri is None else database_uri)

        self.model = {}
        self.schema = "backend."

        self._logger.info(
            f"Generating model tables for website with schema {self.schema}")
        populate_data_instrastructure(
            self.engine, self.schema, self.model)

        self.session_factory = sqlalchemy_utility.get_session_factory(
            self.engine)
        self._logger.info("base created with")
        self._logger.info(f"Classes: {self.base.classes.keys()}")
        self._logger.info(f"Tables: {self.base.metadata.tables.keys()}")
        self.base.prepare(autoload_with=self.engine)

        self.primary_keys = {
            object_class: self.model[object_class].__mapper__.primary_key[0].name for object_class in self.model}
        self._logger.info(f"Datamodel after addition: {self.model}")
        for object_class in self.model:
            self._logger.info(
                f"Object type '{object_class}' currently has {self.get_object_count_by_type(object_class)} registered entries.")
        self._logger.info("Creating new structures")
        # TODO: Implement database population

        self._cache = {
            "active": {}
        }
        self.llm_pool = ThreadedLLMPool()

    def shutdown(self) -> None:
        """
        Method for running shutdown process.
        """
        self.llm_pool.stop_all()
        while any(self.llm_pool.is_running(instance_uuid) for instance_uuid in self._cache):
            sleep(2.0)

    def load_instance(self, instance_uuid: str) -> Optional[str]:
        """
        Method for loading a configured language model instance.
        :param instance_uuid: Instance UUID.
        :return: Instance UUID if process as successful.
        """
        if instance_uuid in self._cache:
            if not self.llm_pool.is_running(instance_uuid):
                self.llm_pool.start(instance_uuid)
                self._cache[instance_uuid]["restarted"] += 1
        else:
            self._cache[instance_uuid] = {
                "started": None,
                "restarted": 0,
                "accessed": 0,
                "inactive": 0
            }
            instance = self.get_object("instance", UUID(instance_uuid))
            llm_config = {
                "model_path": instance.model.path,
                "model_config": {
                    "type": instance.type,
                    "loader": instance.loader,
                    "loader_kwargs": instance.loader_kwargs,
                    "model_version": instance.model_version,
                    "gateway": instance.gateway
                }
            }

            self.llm_pool.prepare_llm(llm_config, instance_uuid)
            self.llm_pool.start(instance_uuid)
            self._cache[instance_uuid]["started"] = dt.now()
        return instance_uuid

    def unload_instance(self, instance_uuid: str) -> Optional[str]:
        """
        Method for unloading a configured language model instance.
        :param instance_uuid: Instance UUID.
        :return: Instance UUID if process as successful.
        """
        if instance_uuid in self._cache:
            if self.llm_pool.is_running(instance_uuid):
                self.llm_pool.stop(instance_uuid)
            return instance_uuid
        else:
            return None

    def forward_generate(self, instance_uuid: str, prompt: str) -> Optional[str]:
        """
        Method for forwarding a generate request to an instance.
        :param instance_uuid: Instance UUID.
        :param prompt: Prompt.
        :return: Instance UUID.
        """
        self.load_instance(instance_uuid)
        return self.llm_pool.generate(instance_uuid, prompt)

    """
    Gateway methods
    """

    def convert_filters(self, entity_type: str, filters: List[FilterMask]) -> list:
        """
        Method for coverting common FilterMasks to SQLAlchemy-filter expressions.
        :param entity_type: Entity type.
        :param filters: A list of Filtermasks declaring constraints.
        :return: Filter expressions.
        """
        filter_expressions = []
        for filtermask in filters:
            filter_expressions.extend([
                sqlalchemy_utility.SQLALCHEMY_FILTER_CONVERTER[exp[1]](getattr(self.model[entity_type], exp[0]),
                                                                       exp[2]) for exp in filtermask.expressions])
        return filter_expressions

    """
    Default object interaction.
    """

    def get_object_count_by_type(self, object_type: str) -> int:
        """
        Method for acquiring object count.
        :param object_type: Target object type.
        :return: Number of objects.
        """
        return int(self.engine.connect().execute(sqlalchemy_utility.select(sqlalchemy_utility.func.count()).select_from(
            self.model[object_type])).scalar())

    def get_objects_by_type(self, object_type: str) -> List[Any]:
        """
        Method for acquiring objects.
        :param object_type: Target object type.
        :return: List of objects of given type.
        """
        return self.session_factory().query(self.model[object_type]).all()

    def get_object_by_id(self, object_type: str, object_id: Any) -> Optional[Any]:
        """
        Method for acquiring objects.
        :param object_type: Target object type.
        :param object_id: Target ID.
        :return: An object of given type and ID, if found.
        """
        return self.session_factory().query(self.model[object_type]).filter(
            getattr(self.model[object_type],
                    self.primary_keys[object_type]) == object_id
        ).first()

    def get_objects_by_filtermasks(self, object_type: str, filtermasks: List[FilterMask]) -> List[Any]:
        """
        Method for acquiring objects.
        :param object_type: Target object type.
        :param filtermasks: Filtermasks.
        :return: A list of objects, meeting filtermask conditions.
        """
        converted_filters = self.convert_filters(object_type, filtermasks)
        with self.session_factory() as session:
            result = session.query(self.model[object_type]).filter(sqlalchemy_utility.SQLALCHEMY_FILTER_CONVERTER["or"](
                *converted_filters)
            ).all()
        return result

    def post_object(self, object_type: str, **object_attributes: Optional[Any]) -> Optional[Any]:
        """
        Method for adding an object.
        :param object_type: Target object type.
        :param object_attributes: Object attributes.
        :return: Object ID of added object, if adding was successful.
        """
        obj = self.model[object_type](**object_attributes)
        with self.session_factory() as session:
            session.add(obj)
            session.commit()
            session.refresh(obj)
        return getattr(obj, self.primary_keys[object_type])

    def patch_object(self, object_type: str, object_id: Any, **object_attributes: Optional[Any]) -> Optional[Any]:
        """
        Method for patching an object.
        :param object_type: Target object type.
        :param object_id: Target ID.
        :param object_attributes: Object attributes.
        :return: Object ID of patched object, if patching was successful.
        """
        result = None
        with self.session_factory() as session:
            obj = session.query(self.model[object_type]).filter(
                getattr(self.model[object_type],
                        self.primary_keys[object_type]) == object_id
            ).first()
            if obj:
                if hasattr(obj, "updated"):
                    obj.updated = dt.now()
                for attribute in object_attributes:
                    setattr(obj, attribute, object_attributes[attribute])
                session.add(obj)
                session.commit()
                result = getattr(obj, self.primary_keys[object_type])
        return result

    def delete_object(self, object_type: str, object_id: Any, force: bool = False) -> Optional[Any]:
        """
        Method for deleting an object.
        :param object_type: Target object type.
        :param object_id: Target ID.
        :param force: Force deletion of the object instead of setting inactivity flag.
        :return: Object ID of deleted object, if deletion was successful.
        """
        result = None
        with self.session_factory() as session:
            obj = session.query(self.model[object_type]).filter(
                getattr(self.model[object_type],
                        self.primary_keys[object_type]) == object_id
            ).first()
            if obj:
                if hasattr(obj, "inanctive") and not force:
                    if hasattr(obj, "updated"):
                        obj.updated = dt.now()
                    obj.inactive = True
                    session.add(obj)
                else:
                    session.delete(obj)
                session.commit()
                result = getattr(obj, self.primary_keys[object_type])
        return result

    """
    Custom methods
    """

    def set_active(self, object_type: str, object_id: Any) -> bool:
        """
        Method for setting active object.
        :param object_type: Object type.
        :param object_id: Object ID.
        :return: True, if successful else False.
        """
        if self.get_object_by_id(object_type, object_id) is not None:
            self._cache["active"][object_type] = object_id
            return True
        else:
            return False

    def embed_document(self, kb_config_id: int, document_content: str) -> int:
        """
        Method for embedding document.
        :param kb_config_id: KB config ID.
        :param document_content: Document content.
        :return: Document ID.
        """
        pass

    def delete_document_embeddings(self, document_id: int) -> int:
        """
        Method for deleting document embeddings.
        :param document_id: Document ID.
        :return: Document ID.
        """
        pass

    def post_query(self, query: str) -> dict:
        """
        Method for posting query.
        :param query: Query.
        :return: Response.
        """
        pass
