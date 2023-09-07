# -*- coding: utf-8 -*-
"""
****************************************************
*                    LLM Tutor                     *
*            (c) 2023 Alexander Hering             *
****************************************************
"""
import os
from typing import Any, List, Dict
import copy
from src.configuration import configuration as cfg
from uuid import uuid4
from src.utility.silver import embedding_utility
from src.utility.bronze.hashing_utility import hash_text_with_sha256
from src.utility.silver.file_system_utility import safely_create_path
from src.model.knowledgebase_control.chromadb_knowledgebase import ChromaKnowledgeBase, KnowledgeBase


class KnowledgeBaseController(object):
    """
    Class, representing a knowledgebase controller.
    """

    def __init__(self, working_directory: str, kb_configs: List[dict], default_embedding_function: Any = None) -> None:
        """
        Initiation method.
        :param working_directory: Working directory.
        :param kb_configs: List of knowledgebase configs for initiation.
        :param default_embedding_function: Default embedding function.
            Defaults to None in which case current utility default is used.
        """
        self.working_directory = working_directory
        self.document_directory = os.path.join(
            self.working_directory, "library")
        safely_create_path(self.document_directory)
        self.default_embedding_function = embedding_utility.LocalHuggingFaceEmbeddings(
            cfg.PATHS.INSTRUCT_XL_PATH
        )
        self.kbs: Dict[str, KnowledgeBase] = {}
        self.documents = {}
        for kb_config in kb_configs:
            self.register_knowledgebase(kb_config)

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

    def delete_document(self, kb: str, document_id: Any, collection: str = "base") -> None:
        """
        Method for deleting a document from the knowledgebase.
        :param kb: Target knowledgebase.
        :param document_id: Document ID.
        :param collection: Collection to remove document from.
        """
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
