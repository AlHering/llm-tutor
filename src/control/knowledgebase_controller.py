# -*- coding: utf-8 -*-
"""
****************************************************
*                    LLM Tutor                     *
*            (c) 2023 Alexander Hering             *
****************************************************
"""
import os
from typing import Any, List
import copy
from src.configuration import configuration as cfg
from src.utility.bronze.hashing_utility import hash_text_with_sha256
from src.utility.silver.file_system_utility import safely_create_path
from src.model.knowledgebase_control.chromadb_knowledgebase import ChromaKnowledgeBase


class KnowledgeBaseController(object):
    """
    Class, representing a knowledgebase controller.
    """

    def __init__(self, document_directory: str, kb_configs: List[dict]) -> None:
        """
        Initiation method.
        :param document_directory: Directory to store documents.
        :param kb_configs: List of knowledgebase configs for initiation.
        """
        self.document_directory = document_directory
        safely_create_path(self.document_directory)
        self.kbs = {}
        self.documents = {}
        for kb_config in kb_configs:
            self.register_knowledgebase(kb_config)

    def register_knowledgebase(self, config: dict) -> None:
        """
        Method for registering knowledgebase.
        :param config: Knowledgebase config.
        """
        pass

    def migrate_knowledgebase(self, source_kb: str, target_kb: str) -> None:
        """
        Method for migrating knowledgebase.
        :param source_kb: Source knowledgebase.
        :param target_kb: Target knowledgebase.
        """
        pass

    def compute_metadata_from_content(self, kb: str, doc_content: str, collection: str = "base") -> dict:
        """
        Method for computing metadata from content.
        :param kb: Target knowledgebase.
        :param doc_content: Document content.
        :param collection: Target collection.
            Defaults to "base".
        """
        return {}

    def embed_documents(self, kb: str, documents: List[str], metadatas: List[dict] = None, ids: List[str] = None, collection: str = "base", compute_metadata: bool = False) -> None:
        """
        Method for embedding documents.
        :param kb: Target knowledgebase.
        :param documents: Documents to embed.
        :param metadatas: Metadata entries for documents.
            Defaults to None.
        :param ids: Custom IDs to add. 
            Defaults to the hash of the document contents.
        :param collection: Target collection.
            Defaults to "base".
        :param compute_metadata: Flag for declaring, whether to compute metadata.
            Defaults to False.
        """
        hashes = [hash_text_with_sha256(document.page_content)
                  for document in documents]
        if metadatas is None:
            if compute_metadata:
                metadatas = [self.compute_metadata_from_content(
                    kb, doc_content, collection) for doc_content in documents]
            elif any(doc_hash in self.documents for doc_hash in hashes):
                metadatas = [self.documents.get(
                    doc_hash, {}) for doc_hash in hashes if doc_hash]

        for doc_index, hash in enumerate(hashes):
            if hash not in self.documents:
                path = os.path.join(self.document_directory, f"{hash}.bin")
                open(os.path.join(self.document_directory, f"{hash}.bin"), "wb").write(
                    documents[doc_index].encode("utf-8"))
                self.documents[hash] = {
                    "metadata": {} if metadatas is None else copy.deepcopy(metadatas[doc_index]),
                    "path": path
                }

        self.kbs[kb].embed_documents(
            collection=collection, documents=documents, metadatas=metadatas, ids=hashes if ids is None else ids)