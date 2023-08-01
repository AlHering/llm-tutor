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


class Model(BaseModel):
    """
    Dataclass for model representation.
    """
    model_uuid: str
    model_path: str
    model_type: str
    model_loader: str


class KnowledgeBase(BaseModel):
    """
    Dataclass for knowledgebase representation.
    """
    knowledgebase_uuid: str
    knowledgebase_path: str
    knowledgebase_loader: str
    embedding_model_uuid: str
    document_uuids: List[str]


class Document(BaseModel):
    """
    Dataclass for documents.
    """
    document_uuid: str
    document_content: str
    document_metadata: dict


class Controller(BaseModel):
    """
    Dataclass for controller representation.
    """
    controller_uuid: str
    language_model_uuid: str
    knowlege_base_uuid: str


class Conversation(BaseModel):
    """
    Dataclass for conversation representation.
    """
    conversation_uuid: str
    controller_uuid: str
    conversation_content: dict


"""
BACKEND ENDPOINTS
"""


class Endpoints(str, Enum):
    """
    String-based endpoint enum class.
    """
    BASE = "/api/v1"
    GET_STATUS = f"{BASE}/status/"
    POST_START = f"{BASE}/start/"

    GET_CONTROLLER = f"{BASE}/controllers/"
    POST_CONTROLLER = f"{BASE}/controllers/"
    PUT_CONTROLLER = f"{BASE}/controllers/{{controller_uuid}}"
    DELETE_CONTROLLER = f"{BASE}/controllers/{{controller_uuid}}"

    GET_MODEL = f"{BASE}/model/"
    POST_MODEL = f"{BASE}/model/"
    PUT_MODEL = f"{BASE}/model/{{model_uuid}}"
    DELETE_MODEL = f"{BASE}/model/{{model_uuid}}"

    GET_KB = f"{BASE}/knowledgebases/"
    POST_KB = f"{BASE}/knowledgebase/"
    PUT_KB = f"{BASE}/knowledgebase/{{knowledgebase_uuid}}"
    DELETE_KB = f"{BASE}/knowledgebase/{{knowledgebase_uuid}}"

    GET_DOCUMENT = f"{BASE}/documents/"
    POST_DOCUMENT = f"{BASE}/documents/"
    PUT_DOCUMENT = f"{BASE}/documents/{{document_uuid}}"
    DELETE_DOCUMENT = f"{BASE}/documents/{{document_uuid}}"

    GET_CONVERSATION = f"{BASE}/conversations/"
    POST_CONVERSATION = f"{BASE}/conversations/"
    PUT_CONVERSATION = f"{BASE}/conversations/{{conversation_uuid}}"
    DELETE_CONVERSATION = f"{BASE}/conversations/{{conversation_uuid}}"

    POST_LOAD_CONTROLLER = f"{BASE}/controllers/{{controller_uuid}}/load"
    POST_UNLOAD_CONTROLLER = f"{BASE}/controllers/{{controller_uuid}}/unload"

    POST_CONVERSATION_QUERY = f"{BASE}/conversation/{{conversation_uuid}}/query/{{query}}"
    POST_DIRECT_QUERY = f"{BASE}/controllers/{{controller_uuid}}/load"

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
