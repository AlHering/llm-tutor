# -*- coding: utf-8 -*-
"""
****************************************************
*                   Utility
*            (c) 2023 Alexander Hering             *
****************************************************
"""
import os
from .filter_mask import FilterMask
from ..bronze import sqlalchemy_utility
from datetime import datetime as dt
from typing import Optional, Any, List


class BasicSQLAlchemyInterface(object):
    """
    Class, representing a basic SQL Alchemy interface.
    """

    def __init__(self, working_directory: str, database_uri: str, population_function: Any, logger: Any = None) -> None:
        """
        Initiation method.
        :param working_directory: Working directory.
        :param database_uri: Database URI.
        :param population_function: A function, taking an engine, schema and a dataclass dictionary (later one can be empty and is to be populated).
        :param logger: Logger instance. 
            Defaults to None in which case separate logging is disabled.
        """
        self._logger = logger
        self.working_directory = working_directory
        if not os.path.exists(self.working_directory):
            os.makedirs(self.working_directory)
        self.database_uri = database_uri
        self.population_function = population_function

        # Database infrastructure
        self.base = None
        self.engine = None
        self.model = None
        self.schema = None
        self.session_factory = None
        self.primary_keys = None
        self._setup_database()

    def _setup_database(self) -> None:
        """
        Internal method for setting up database infastructure.
        """
        if self.logger is not None:
            self._logger.info("Automapping existing structures")
        self.base = sqlalchemy_utility.automap_base()
        self.engine = sqlalchemy_utility.get_engine(self.database_uri)

        self.model = {}
        self.schema = "backend."

        if self.logger is not None:
            self._logger.info(
                f"Generating model tables for website with schema {self.schema}")
        self.population_function(
            self.engine, self.schema, self.model)

        self.base.prepare(autoload_with=self.engine)
        self.session_factory = sqlalchemy_utility.get_session_factory(
            self.engine)
        if self.logger is not None:
            self._logger.info("base created with")
            self._logger.info(f"Classes: {self.base.classes.keys()}")
            self._logger.info(f"Tables: {self.base.metadata.tables.keys()}")

        self.primary_keys = {
            object_class: self.model[object_class].__mapper__.primary_key[0].name for object_class in self.model}
        if self.logger is not None:
            self._logger.info(f"Datamodel after addition: {self.model}")
            for object_class in self.model:
                self._logger.info(
                    f"Object type '{object_class}' currently has {self.get_object_count_by_type(object_class)} registered entries.")

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
