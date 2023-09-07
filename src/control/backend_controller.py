# -*- coding: utf-8 -*-
"""
****************************************************
*          Basic Language Model Backend            *
*            (c) 2023 Alexander Hering             *
****************************************************
"""
import os
from uuid import UUID, uuid4
from time import sleep
from datetime import datetime as dt
from typing import Optional, Any, List, Dict
from src.configuration import configuration as cfg
from src.utility.gold.basic_sqlalchemy_interface import BasicSQLAlchemyInterface
from src.utility.bronze import sqlalchemy_utility
from src.utility.bronze.hashing_utility import hash_text_with_sha256
from src.model.backend_control.data_model import populate_data_instrastructure
from src.model.backend_control.llm_pool import ThreadedLLMPool
from src.utility.silver import embedding_utility
from src.utility.bronze.hashing_utility import hash_text_with_sha256
from src.utility.silver.file_system_utility import safely_create_path
from src.model.knowledgebase_control.chromadb_knowledgebase import ChromaKnowledgeBase, KnowledgeBase


class BackendController(BasicSQLAlchemyInterface):
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
        # Main instance variables
        self._logger = cfg.LOGGER
        self.working_directory = cfg.PATHS.BACKEND_PATH if working_directory is None else working_directory
        if not os.path.exists(self.working_directory):
            os.makedirs(self.working_directory)
        self.database_uri = f"sqlite:///{os.path.join(cfg.PATHS.DATA_PATH, 'backend.db')}" if database_uri is None else database_uri

        # Database infrastructure
        super().__init__(self.working_directory, self.database_uri,
                         populate_data_instrastructure, self._logger)
        self.base = None
        self.engine = None
        self.model = None
        self.schema = None
        self.session_factory = None
        self.primary_keys = None
        self._setup_database()

        # Knowledgebase infrastructure
        self.document_directory = os.path.join(
            self.working_directory, "library")
        safely_create_path(self.document_directory)
        self.default_embedding_function = embedding_utility.LocalHuggingFaceEmbeddings(
            cfg.PATHS.INSTRUCT_XL_PATH
        )
        self.kbs: Dict[str, KnowledgeBase] = {}
        self.documents = {}
        for kb_config in self.get_objects_by_type("kb_config"):
            self.register_knowledgebase(kb_config)

        # LLM infrastructure
        self.llm_pool = ThreadedLLMPool()

        # Cache
        self._cache = {
            "active": {}
        }

    """
    Setup and population methods
    """

    def _setup_database(self) -> None:
        """
        Internal method for setting up database infastructure.
        """
        self._logger.info("Automapping existing structures")
        self.base = sqlalchemy_utility.automap_base()
        self.engine = sqlalchemy_utility.get_engine(
            f"sqlite:///{os.path.join(cfg.PATHS.DATA_PATH, 'backend.db')}" if self.database_uri is None else self.database_uri)

        self.model = {}
        self.schema = "backend."

        self._logger.info(
            f"Generating model tables for website with schema {self.schema}")
        populate_data_instrastructure(
            self.engine, self.schema, self.model)

        self.base.prepare(autoload_with=self.engine)
        self.session_factory = sqlalchemy_utility.get_session_factory(
            self.engine)
        self._logger.info("base created with")
        self._logger.info(f"Classes: {self.base.classes.keys()}")
        self._logger.info(f"Tables: {self.base.metadata.tables.keys()}")

        self.primary_keys = {
            object_class: self.model[object_class].__mapper__.primary_key[0].name for object_class in self.model}
        self._logger.info(f"Datamodel after addition: {self.model}")
        for object_class in self.model:
            self._logger.info(
                f"Object type '{object_class}' currently has {self.get_object_count_by_type(object_class)} registered entries.")

    """
    Exit and shutdown methods
    """

    def shutdown(self) -> None:
        """
        Method for running shutdown process.
        """
        self.llm_pool.stop_all()
        while any(self.llm_pool.is_running(instance_uuid) for instance_uuid in self._cache):
            sleep(2.0)

    """
    LLM handling methods
    """

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
    Knowledgebase handling methods
    """

    def register_knowledgebase(self, config: dict) -> str:
        """
        Method for registering knowledgebase.
        :param config: Knowledgebase config.
        :return: Knowledgebase name.
        """
        name = config.get("name", uuid4())
        handler = config.get("handler", "chromadb")
        handler_kwargs = config.get("handler_kwargs", {
            "peristant_directory": os.path.join(self.working_directory, name),
            "base_embedding_function": self.default_embedding_function,
            "implementation": "duckdb+parquet"}
        )

        self.kbs[name] = {"chromadb": ChromaKnowledgeBase}[handler](
            **handler_kwargs
        )
        return name

    def delete_documents(self, kb: str, document_ids: List[Any], collection: str = "base") -> None:
        """
        Method for deleting a document from the knowledgebase.
        :param kb: Target knowledgebase.
        :param document_ids: Document IDs.
        :param collection: Collection to remove document from.
        """
        for document_id in document_ids:
            self.kbs[kb].delete_document(document_id, collection)

    def wipe_knowledgebase(self, target_kb: str) -> None:
        """
        Method for wiping a knowledgebase.
        :param target_kb: Target knowledgebase.
        """
        self.kbs[target_kb].wipe_knowledgebase()

    def migrate_knowledgebase(self, source_kb: str, target_kb: str) -> None:
        """
        Method for migrating knowledgebase.
        :param source_kb: Source knowledgebase.
        :param target_kb: Target knowledgebase.
        """
        pass

    def embed_documents(self, kb: str, documents: List[str], metadatas: List[dict] = None, ids: List[str] = None, hashes: List[str] = None, collection: str = "base", compute_metadata: bool = False) -> None:
        """
        Method for embedding documents.
        :param kb: Target knowledgebase.
        :param documents: Documents to embed.
        :param metadatas: Metadata entries for documents.
            Defaults to None.
        :param ids: Custom IDs to add. 
            Defaults to the hash of the document contents.
        :param hashes: Content hashes.
            Defaults to None in which case hashes are computet.
        :param collection: Target collection.
            Defaults to "base".
        :param compute_metadata: Flag for declaring, whether to compute metadata.
            Defaults to False.
        """
        hashes = [hash_text_with_sha256(document.page_content)
                  for document in documents] if hashes is None else hashes
        for doc_index, hash in enumerate(hashes):
            if hash not in self.documents:
                path = os.path.join(self.document_directory, f"{hash}.bin")
                open(os.path.join(self.document_directory, f"{hash}.bin"), "wb").write(
                    documents[doc_index].encode("utf-8"))
                self.documents[hash] = {
                } if metadatas is None else metadatas[doc_index]
                self.documents[hash]["controller_library_path"] = path

        if metadatas is None:
            metadatas = [self.documents[hash] for hash in hashes]

        self.kbs[kb].embed_documents(
            collection=collection, documents=documents, metadatas=metadatas, ids=hashes if ids is None else ids)

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

    def embed_document(self, kb_config_id: int, document_content: str, document_metadata: dict = None) -> int:
        """
        Method for embedding document.
        :param kb_config_id: KB config ID.
        :param document_content: Document content.
        :param document_metadata: Document metadata.
            Defaults to None
        :return: Document ID.
        """
        kb_config = self.get_object_by_id("kb_config", kb_config_id)
        doc_id = self.post_object("document", {
            "content": document_content,
            "kb_config_id": kb_config.id
        })
        document_metadata = {} if document_metadata is None else document_metadata
        document_metadata.update({
            "hash": hash_text_with_sha256(document_content),
            "kb_id": kb_config.id,
            "kb_name": kb_config.config["name"]
        })

        self.kb_controller.embed_documents(
            kb_config["name"], documents=[document_content],
            metadatas=[document_metadata],
            ids=[str(doc_id)],
            hashes=[document_metadata["hash"]]
        )
        return doc_id

    def delete_document_embeddings(self, document_id: int) -> int:
        """
        Method for deleting document embeddings.
        :param document_id: Document ID.
        :return: Document ID.
        """
        doc = self.get_object_by_id("document", document_id)
        self.kb_controller.delete_documents(
            doc.kb_config.config["name"],
            [str(doc.id)]
        )

    def post_query(self, query: str) -> dict:
        """
        Method for posting query.
        :param query: Query.
        :return: Response.
        """
        pass
