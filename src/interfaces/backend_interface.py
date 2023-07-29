# -*- coding: utf-8 -*-
"""
****************************************************
*                    LLM Tutor                     *
*            (c) 2023 Alexander Hering             *
****************************************************
"""
import uvicorn
import os
from typing import Union, List, Optional, Any
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


@BACKEND.get("/")
def get_home() -> dict:
    """
    Home endpoint for getting system status.
    :return: Response.
    """
    global STARTED
    global CONTROLLER
    return {"message": f"System is {'started' if STARTED else 'stopped'}"}


@BACKEND.post("/start")
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


@BACKEND.post("/load_llm")
def post_load_llm(llm_description: LLMDescription) -> dict:
    """
    Endpoint for loading models.
    param llm_description: LLM description configuring loading parameters.
    :return: Response.
    """
    global STARTED
    global CONTROLLER
    if STARTED == True:
        CONTROLLER.load_general_llm(**llm_description.dict())
        return {"message": f"LLM loaded."}
    else:
        return {"message": f"System is stopped!"}


@BACKEND.post("/load_kb")
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
        return {"message": f"Knowledgebase loaded."}
    else:
        return {"message": f"System is stopped!"}


@BACKEND.post("/embed")
def post_embed(docs: DocumentList) -> dict:
    """
    Endpoint for embedding a list of documents.
    param docs: List of documents to embed.
    :return: Response.
    """
    global STARTED
    global CONTROLLER
    if STARTED == True:
        if CONTROLLER.kb is not None:
            CONTROLLER.load_documents(docs.documents)
            return {"message": f"Documents loaded."}
        else:
            return {"message": f"No knowledgebase loaded!"}
    else:
        return {"message": f"System is stopped!"}


@BACKEND.post("/start_conversation")
def post_start_conversation(conversation_uuid: str = None) -> dict:
    """
    Endpoint for starting conversation.
    param conversation_uuid: UUID to start conversation with. Defaults to None in which case a UUID is generated.
    :return: Response.
    """
    global STARTED
    global CONTROLLER
    if STARTED == True:
        if CONTROLLER.kb is not None:
            return {"result": CONTROLLER.start_conversation(conversation_uuid)}
        else:
            return {"message": f"No knowledgebase loaded!"}
    else:
        return {"message": f"System is stopped!"}


@BACKEND.post("/query_conversation")
def post_query(query: str, conversation_uuid: str = None) -> dict:
    """
    Endpoint for sending query into conversation.
    param query: Query to send.
    :param conversation_uuid: UUID of conversation to send query to. Defaults to None in which case a new conversation ist started.
    :return: Response.
    """
    global STARTED
    global CONTROLLER
    if STARTED == True:
        if CONTROLLER.kb is not None:
            return {"result": CONTROLLER.conversational_query(conversation_uuid, query)}
        else:
            return {"message": f"No knowledgebase loaded!"}
    else:
        return {"message": f"System is stopped!"}


@BACKEND.post("/query")
def post_query(query: str) -> dict:
    """
    Endpoint for querying knowledgebase.
    param query: Query to send.
    :return: Response.
    """
    global STARTED
    global CONTROLLER
    if STARTED == True:
        if CONTROLLER.kb is not None:
            return {"result": CONTROLLER.query(query)}
        else:
            return {"message": f"No knowledgebase loaded!"}
    else:
        return {"message": f"System is stopped!"}


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
