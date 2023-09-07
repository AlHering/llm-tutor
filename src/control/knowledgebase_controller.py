# -*- coding: utf-8 -*-
"""
****************************************************
*                    LLM Tutor                     *
*            (c) 2023 Alexander Hering             *
****************************************************
"""
import os
from typing import Any, List
from src.configuration import configuration as cfg
from src.utility.bronze.hashing_utility import hash_text_with_sha256
from src.model.knowledgebase_control.chromadb_knowledgebase import ChromaKnowledgeBase


class KnowledgeBaseController(object):
    """
    Class, representing a knowledgebase controller.
    """

    def __init__(self, kb_configs: List[dict]) -> None:
        """
        Initiation method.
        :param kb_configs: List of knowledgebase configs for initiation.
        """
        self.kbs = {}
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

    def embed_documents(self, kb: str, documents: List[str], metadatas: List[dict], ids: List[str] = None, collection: str = "base") -> None:
        """
        Method for embedding documents.
        :param kb: Target knowledgebase.
        :param name: Collection to use.
        :param documents: Documents to embed.
        :param metadatas: Metadata entries for documents.
        :param ids: Custom IDs to add. Defaults to the hash of the document contents.
        :param collection: Target collection.
        """
        self.kbs[kb].embed_documents(collection=collection, documents=documents, ids=[
            hash_text_with_sha256(document.page_content) for document in documents] if ids is None else ids)
