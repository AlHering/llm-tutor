# -*- coding: utf-8 -*-
"""
****************************************************
*                    LLM Tutor                     *
*            (c) 2023 Alexander Hering             *
****************************************************
"""
import uvicorn
import os
from enum import Enum
from typing import Union, List, Optional, Any, Dict
from fastapi import FastAPI
from pydantic import BaseModel
from uuid import uuid4
from src.configuration import configuration as cfg
from src.control.tutor_controller import TutorController

"""
BACKEND CONTROL
"""
BACKEND = FastAPI(title="LLMTutor Backend", version="0.1",
                  description="LLM-powered backend for document embedding an querying.")
STARTED = False
CONTROLLER: TutorController = None


"""
DATA CLASSES
"""


class LLMDescription(BaseModel):
    """
    Dataclass for LLM descrions.
    """
    model_path: str
    model_type: str


class Document(BaseModel):
    """
    Dataclass for documents.
    """
    page_content: str
    metadata: dict


class DocumentList(BaseModel):
    """
    Dataclass for a document list.
    """
    documents: List[Document]


"""
BACKEND ENDPOINTS
"""


class Endpoints(str, Enum):
    """
    String-based endpoint enum class.
    """
    GET_ROOT = "/"
    POST_START = "/start"
    GET_CONFIGS = "/configs"
    POST_SAVE_CONFIG = "/save_config"
    POST_LOAD_CONFIG = "/load_config"
    POST_LOAD_LLM = "/load_llm"
    POST_LOAD_KB = "/load_kb"
    POST_EMBED = "/embed"
    POST_START_CONVERSATION = "/start_conversation"
    POST_CONVERSATION_QUERY = "/conversation_query"
    POST_QUERY = "/query"

    def __str__(self) -> str:
        """
        Getter method for a string representation.
        """
        return self.value


@BACKEND.get(Endpoints.GET_ROOT)
def get_status() -> dict:
    """
    Root endpoint for getting system status.
    :return: Response.
    """
    global STARTED
    global CONTROLLER
    return {"message": f"System is {'started' if STARTED else 'stopped'}"}


@BACKEND.post(Endpoints.POST_START)
def post_start() -> dict:
    """
    Endpoint for starting system.
    :return: Response.
    """
    global STARTED
    global CONTROLLER
    if STARTED == False:
        CONTROLLER = TutorController()
        STARTED = True
    return {"message": f"System is {'started' if STARTED else 'stopped'}"}


@BACKEND.get(Endpoints.GET_CONFIGS)
def get_configs() -> dict:
    """
    Endpoint retrieving available configs.
    :return: Response.
    """
    global STARTED
    global CONTROLLER
    if STARTED == True:
        return {"configs": CONTROLLER.get_available_configs()}
    else:
        return {"message": "System is stopped!"}


@BACKEND.post(Endpoints.POST_SAVE_CONFIG)
def post_save_config(config_name: str) -> dict:
    """
    Endpoint for saving config.
    :param config_name: Name to save config under.
    :return: Response.
    """
    global STARTED
    global CONTROLLER
    if STARTED == True:
        CONTROLLER.save_config(config_name)
        return {"message": f"Config '{config_name}' saved."}
    else:
        return {"message": "System is stopped!"}


@BACKEND.post(Endpoints.POST_LOAD_CONFIG)
def post_load_config(config_name: str) -> dict:
    """
    Endpoint for loading config.
    :param config_name: Name of config to load.
    :return: Response.
    """
    global STARTED
    global CONTROLLER
    if STARTED == True:
        CONTROLLER.load_config(config_name)
        return {"message": f"Config '{config_name}' loaded."}
    else:
        return {"message": "System is stopped!"}


@BACKEND.post(Endpoints.POST_LOAD_LLM)
def post_load_llm(llm_description: LLMDescription) -> dict:
    """
    Endpoint for loading models.
    :param llm_description: LLM description configuring loading parameters.
    :return: Response.
    """
    global STARTED
    global CONTROLLER
    if STARTED == True:
        CONTROLLER.load_general_llm(**llm_description.dict())
        return {"message": "LLM loaded."}
    else:
        return {"message": "System is stopped!"}


@BACKEND.post(Endpoints.POST_LOAD_KB)
def post_load_kb() -> dict:
    """
    Endpoint for loading a knowledge base.
    :return: Response.
    """
    global STARTED
    global CONTROLLER
    if STARTED == True:
        CONTROLLER.load_knowledge_base(os.path.join(
            cfg.PATHS.DATA_PATH, "backend", "kb"))
        return {"message": "Knowledgebase loaded."}
    else:
        return {"message": "System is stopped!"}


@BACKEND.post(Endpoints.POST_EMBED)
def post_embed(docs: DocumentList, collection: str = None) -> dict:
    """
    Endpoint for embedding a list of documents.
    :param docs: List of documents to embed.
    :param collection: Collection to embed documents in. Defaults to None in which case default the collection is set.
    :return: Response.
    """
    global STARTED
    global CONTROLLER
    if STARTED == True:
        if CONTROLLER.kb is not None:
            CONTROLLER.load_documents(docs.documents, collection)
            return {"message": "Documents loaded."}
        else:
            return {"message": "No knowledgebase loaded!"}
    else:
        return {"message": "System is stopped!"}


@BACKEND.post(Endpoints.POST_START_CONVERSATION)
def post_start_conversation(conversation_uuid: str = None, collection: str = None) -> dict:
    """
    Endpoint for starting conversation.
    :param conversation_uuid: UUID to start conversation with. Defaults to None in which case a UUID is generated.
    :param collection: Collection to embed documents in. Defaults to None in which case default the collection is set.
    :return: Response.
    """
    global STARTED
    global CONTROLLER
    if STARTED == True:
        if CONTROLLER.kb is not None:
            return {"conversation": CONTROLLER.start_conversation(conversation_uuid, collection)}
        else:
            return {"message": "No knowledgebase loaded!"}
    else:
        return {"message": "System is stopped!"}


@BACKEND.post(Endpoints.POST_CONVERSATION_QUERY)
def post_conversation_query(query: str, conversation_uuid: str = None) -> dict:
    """
    Endpoint for sending query into conversation.
    :param query: Query to send.
    :param conversation_uuid: UUID of conversation to send query to. Defaults to None in which case a new conversation ist started.
    :return: Response.
    """
    global STARTED
    global CONTROLLER
    if STARTED == True:
        if CONTROLLER.kb is not None:
            return {"result": CONTROLLER.conversational_query(conversation_uuid, query)}
        else:
            return {"message": "No knowledgebase loaded!"}
    else:
        return {"message": "System is stopped!"}


@BACKEND.post(Endpoints.POST_QUERY)
def post_query(query: str, collection: str = None, include_source: bool = True) -> dict:
    """
    Endpoint for querying knowledgebase.
    :param query: Query to send.
    :param collection: Collection to embed documents in. Defaults to None in which case default the collection is set.
    :param include_source: Flag for declaring whether to include source. Defaults to True.
    :return: Response.
    """
    global STARTED
    global CONTROLLER
    if STARTED == True:
        if CONTROLLER.kb is not None:
            return {"result": CONTROLLER.query(query, collection, include_source)}
        else:
            return {"message": "No knowledgebase loaded!"}
    else:
        return {"message": "System is stopped!"}


"""
BACKEND RUNNERS
"""


def run_backend(host: str = None, port: int = None, reload: bool = True) -> None:
    """
    Function for running backend server.
    :param host: Server host. Defaults to None in which case "127.0.0.1" is set.
    :param port: Server port. Defaults to None in which case either environment variable "BACKEND_PORT" is set or 7861.
    :param reload: Reload flag for server. Defaults to True.
    """
    uvicorn.run("src.interfaces.backend_interface:BACKEND",
                host="127.0.0.1" if host is None else host,
                port=int(
                    cfg.ENV.get("BACKEND_PORT", 7861) if port is None else port),
                reload=True)


if __name__ == "__main__":
    run_backend()
