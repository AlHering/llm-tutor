
# -*- coding: utf-8 -*-
"""
****************************************************
*                    LLM Tutor                     *
*            (c) 2023 Alexander Hering             *
****************************************************
"""
from typing import Any, List, Tuple
from langchain.llms import LlamaCpp
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.chains import RetrievalQA
from langchain.indexes import VectorstoreIndexCreator
from uuid import uuid4
from src.control.chroma_knowledgebase_controller import ChromaKnowledgeBase, EmbeddingFunction, Embeddings, Document


class TutorController(object):
    """
    Class for controlling the main process.
    """

    def __init__(self) -> None:
        """
        Initiation method.
        """
        self.llm = None
        self.llm_type = None
        self.interface = None
        self.kb = None
        self.doc_types = {
            "base": {"splitting": None}
        }
        self.conversations = {}

    def load_general_llm(self, model_path: str, model_type: str) -> None:
        """
        Method for (re)loading main LLM.
        :param model_path: Model path.
        :param model_type: Model type frmo 'llm', 'chat', 'instruct'
        """
        self.llm = LlamaCpp(
            model_path=model_path,
            verbose=True,
            n_ctx=2048)

    def load_knowledge_base(self, kb_path: str, kb_base_embedding_function: EmbeddingFunction = None) -> None:
        """
        Method for loading knowledgebase.
        :param kb_path: Folder path to knowledgebase.
        :param kb_base_embedding_function: Base embedding function to use for knowledgebase. 
            Defaults to None in which case the knowledgebase default is used.
        """
        self.kb = ChromaKnowledgeBase(
            peristant_directory=kb_path, base_embedding_function=kb_base_embedding_function)

    def register_document_type(self, document_type: str, embedding_function: EmbeddingFunction = None, splitting: Tuple[int] = None) -> None:
        """
        Method for registering a document type.
        :param document_type: Name to identify the documen type.
        :param embedding_function: Embedding function the document type. Defaults to base embedding function.
        :param splitting: A tuple of chunk size and overlap for splitting. Defaults to None in which case the documents are not split.
        """
        self.doc_types[document_type] = {"splitting": splitting}
        self.kb.get_or_create_collection(
            document_type, embedding_function)

    def load_documents(self, documents: List[Document], document_type: str = "base") -> None:
        """
        Method for loading documents into knowledgebase.
        :param documents: Documents to load.
        :param document_type: Name to identify the documen type. Defaults to "base".
        """
        self.kb.embed_documents(
            name=document_type, documents=documents)

    def load_files(self, file_paths: List[str], document_type: str = "base") -> None:
        """
        Method for (re)loading folder contents.
        :param folder: Folder path.
        :param document_type: Name to identify the documen type. Defaults to "base".
        """
        self.kb.load_files(file_paths, document_type, self.doc_types.get(
            document_type, {}).get("splitting"))

    def start_conversation(self, use_uuid: str = None, document_type: str = "base") -> str:
        """
        Method for starting conversation.
        :param use_uuid: UUID to start conversation under. Defaults to newly generated UUID.
        :param document_type: Target document type. Defaults to "base".
        :return: Conversation UUID.
        """
        uuid = str(uuid4()) if use_uuid is None else use_uuid
        memory = ConversationBufferMemory(
            memory_key=f"chat_history", return_messages=True)
        self.conversations[uuid] = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=self.kb.get_retriever(document_type),
            memory=memory
        )
        return uuid

    def query(self, conversation_uuid: str, query: str) -> dict:
        """
        Method for querying via conversation.
        :param conversation_uuid: UUID of conversation to run query on.
        :param query: Query to run.
        :return: Query results.
        """
        if conversation_uuid not in self.conversations:
            self.start_conversation(use_uuid=conversation_uuid)
        return self.conversations[conversation_uuid]({"question": query})
