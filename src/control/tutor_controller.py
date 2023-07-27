
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
from src.control.knowledgebase_controller import KnowledgeBaseController, EmbeddingFunction, Embeddings, Document


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
        self.knowledge_base = None
        self.doc_types = {
            "base": {"splitting": None}
        }

    def load_general_llm(self, model_path: str, model_type: str) -> None:
        """
        Method for (re)loading main LLM.
        :param model_path: Model path.
        :param model_type: Model type frmo 'llm', 'chat', 'instruct'
        """
        self.llm = LlamaCpp(
            model_path=model_path,
            verbose=True)
        
    def load_knowledge_base(self, kb_path: str, kb_base_embedding_function: EmbeddingFunction) -> None:
        """
        Method for loading knowledgebase.
        :param kb_path: Folder path to knowledgebase.
        :param kb_base_embedding_function: Base embedding function to use for knowledgebase.
        """
        self.knowledge_base = KnowledgeBaseController(peristant_directory=kb_path, base_embedding_function=kb_base_embedding_function)

    def register_document_type(self, documen_type: str, embedding_function: EmbeddingFunction = None, splitting: Tuple[int] = None) -> None:
        """
        Method for registering a document type.
        :param documen_type: Name to identify the documen type.
        :param embedding_function: Embedding function the document type. Defaults to base embedding function.
        :param splitting: A tuple of chunk size and overlap for splitting. Defaults to None in which case the documents are not split.
        """
        self.doc_types[documen_type] = {"splitting": splitting}
        self.knowledge_base.get_or_create_client(documen_type, embedding_function)

        
    def load_documents(self, documents: List[Document], document_type: str = "base") -> None:
        """
        Method for loading documents into knowledgebase.
        :param documents: Documents to load.
        :param document_type: Name to identify the documen type. Defaults to "base".
        """
        self.knowledge_base.embed_documents(name=document_type, documents=documents)

    def load_files(self, file_paths: List[str], document_type: str = "base") -> None:
        """
        Method for (re)loading folder contents.
        :param folder: Folder path.
        :param document_type: Name to identify the documen type. Defaults to "base".
        """
        self.knowledge_base.load_files(file_paths, document_type, self.doc_types.get(document_type, {}).get("splitting"))

    def start_conversation(self):
        """
        Method for starting conversation.
        """
        memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        conversation_chain = ConversationalRetrievalChain(
            llm=self.llm,
            retriever=self.knowledge_base.get_retriever(),
            memory=memory
        )

