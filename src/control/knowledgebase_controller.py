# -*- coding: utf-8 -*-
"""
****************************************************
*                    LLM Tutor                     *
*            (c) 2023 Alexander Hering             *
****************************************************
"""
import os
from typing import Any, List, Tuple
from chromadb.api.types import EmbeddingFunction, Embeddings
from chromadb.config import Settings
from langchain.vectorstores import Chroma
from langchain.docstore.document import Document
from langchain.vectorstores.base import VectorStoreRetriever
from src.utility.bronze.hashing_utility import hash_text_with_sha256
from langchain.chains import RetrievalQA
from langchain.text_splitter import RecursiveCharacterTextSplitter
from multiprocessing import Pool
from tqdm import tqdm
from src.utility import langchain_utility


def reload_document(document_path: str) -> Document:
    """
    Function for (re)loading document content.
    :param document_path: Document path.
    :return: Document object.
    """
    res = langchain_utility.DOCUMENT_LOADERS[os.path.splitext(document_path)[
        1]](document_path).load()
    return res[0] if isinstance(res, list) and len(res) == 1 else res


class KnowledgeBaseController(object):
    """
    Class for hanling knowledge base interaction.
    """
    def __init__(self, peristant_directory: str, base_embedding_function: EmbeddingFunction) -> None:
        """
        Initiation method.
        :param peristant_directory: Persistant directory for ChromaDB data.
        :param base_embedding_function: Embedding function for base client.
        """
        if not os.path.exists(peristant_directory):
            os.makedirs(peristant_directory)
        self.peristant_directory = peristant_directory
        self.base_embedding_function = base_embedding_function
        self.client_settings = Settings(
            chroma_api_impl="duckdb+parquet",
            persist_directory=peristant_directory,

        )
        self.default_client = Chroma(
                    collection_name="base",
                    persist_directory=peristant_directory,
                    client_settings=self.client_settings,
                    embedding_function=self.base_embedding_function
                )
        self.clients = {
            "base": self.default_client
        }
        
    def get_or_create_client(self, name: str, embedding_function: EmbeddingFunction = None) -> Chroma:
        """
        Method for adding database.
        :param name: Name to identify client and its collection.
        :param embedding_function: Embedding function the client. Defaults to base embedding function.
        :return: Persistant chromadb client.
        """
        if name not in self.clients:
            self.clients[name] = Chroma(
                    collection_name=name,
                    persist_directory=self.peristant_directory,
                    client_settings=self.client_settings,
                    embedding_function=self.base_embedding_function if embedding_function is None else embedding_function
                )
        return self.clients[name]
    
    def get_retriever(self, name: str, search_type: str = "similarity", search_kwargs: dict = {"k": 4, "include_metadata": True}) -> VectorStoreRetriever:
        """
        Method for acquiring a retriever.
        :param name: Client and collection to use.
        :param search_type: The retriever's search type. Defaults to "similarity".
        :param search_kwargs: The retrievery search keyword arguments. Defaults to {"k": 4, "include_metadata": True}.
        :return: Retriever instance.
        """
        self.clients.get(name, self.clients["base"]).as_retriever(
            search_type=search_type, search_kwargs=search_kwargs
        )

    def embed_documents(self, name: str, documents: List[Document], ids: List[str] = None):
        """
        Method for embedding documents.
        :param name: Client and collection to use.
        :param documents: Documents to embed.
        :param ids: Custom IDs to add. Defaults to the hash of the document contents.
        """
        self.clients.get(name, self.clients["base"]).add_documents(documents=documents, ids=[[hash_text_with_sha256(document.page_content) for document in documents]] if ids is None else ids)

    def load_folder(self, folder: str, target_client: str = "base", splitting: Tuple[int] = None) -> None:
        """
        Method for (re)loading folder contents.
        :param folder: Folder path.
        :param target_client: Client/collection to handle folder contents. Defaults to "base".
        :param splitting: A tuple of chunk size and overlap for splitting. Defaults to None in which case the documents are not split.
        """
        file_paths = []
        for root, dirs, files in os.walk(folder, topdown=True):
            file_paths.extend([os.path.join(root, file) for file in files])

        self.load_files(file_paths, target_client, splitting)

    def load_files(self, file_paths: List[str], target_client: str = "base", splitting: Tuple[int] = None) -> None:
        """
        Method for (re)loading file paths.
        :param file_paths: List of file paths.
        :param target_client: Client/collection to handle folder contents. Defaults to "base".
        :param splitting: A tuple of chunk size and overlap for splitting. Defaults to None in which case the documents are not split.
        """
        document_paths = [file for file in file_paths if any(file.lower().endswith(
                supported_extension) for supported_extension in langchain_utility.DOCUMENT_LOADERS)]
        documents = []

        with Pool(processes=os.cpu_count()) as pool:
            with tqdm(total=len(document_paths), desc="(Re)loading folder contents...", ncols=80) as progress_bar:
                for index, loaded_document in enumerate(pool.imap(reload_document, document_paths)):
                    documents.append(loaded_document)
                    progress_bar.update(index)

        if splitting is not None:
            documents = self.split_documents(documents, *splitting)

        self.embed_documents(target_client, documents)

    def split_documents(self, documents: List[Document], split: int, overlap: int) -> List[Document]:
        """
        Method for splitting document content.
        :param documents: Documents to split.
        :param split: Chunk size to split documents into.
        :param overlap: Overlap for split chunks.
        :return: Split documents.
        """
        return RecursiveCharacterTextSplitter(
            chunk_size=self.profile["splitting_chunks"],
            chunk_overlap=self.profile["splitting_overlap"],
            length_function=len).split_documents(documents)