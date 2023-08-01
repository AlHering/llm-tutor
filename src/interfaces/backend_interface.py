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
from functools import wraps
from src.configuration import configuration as cfg
from src.control.tutor_controller import TutorController

"""
Backend control
"""
BACKEND = FastAPI(title="LLMTutor Backend", version="0.1",
                  description="LLM-powered backend for document embedding an querying.")
STATUS = False
CONTROLLER: TutorController = None


def access_validator(status: bool) -> Optional[Any]:
    """
    Validation decorator.
    :param func: Decorated function.
    :param status: Status to check.
    :return: Error message if status is incorrect, else function return.
    """
    global STATUS

    def wrapper(func: Any) -> Optional[Any]:
        """
        Function wrapper.
        :param func: Wrapped function.
        :return: Error message if status is incorrect, else function return.
        """
        @wraps(func)
        async def inner(*args: Optional[Any], **kwargs: Optional[Any]):
            """
            Inner function wrapper.
            :param args: Arguments.
            :param kwargs: Keyword arguments.
            """
            if status != STATUS:
                return {"message": f"System is {' already started' if STATUS else 'currently stopped'}"}
            else:
                return await func(*args, **kwargs)
        return inner
    return wrapper


"""
Dataclasses
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
    POST_STOP = f"{BASE}/stop/"

    GET_CONTROLLERS = f"{BASE}/controllers/"
    GET_CONTROLLER = f"{BASE}/controller/{{controller_uuid}}"
    POST_CONTROLLER = f"{BASE}/controller/"
    PATCH_CONTROLLER = f"{BASE}/controller/{{controller_uuid}}"
    DELETE_CONTROLLER = f"{BASE}/controller/{{controller_uuid}}"

    GET_MODELS = f"{BASE}/models/"
    GET_MODEL = f"{BASE}/model/"
    POST_MODEL = f"{BASE}/model/"
    PATCH_MODEL = f"{BASE}/model/{{model_uuid}}"
    DELETE_MODEL = f"{BASE}/model/{{model_uuid}}"

    GET_KBS = f"{BASE}/knowledgebases/"
    GET_KB = f"{BASE}/knowledgebase/{{knowledgebase_uuid}}"
    POST_KB = f"{BASE}/knowledgebase/"
    PATCH_KB = f"{BASE}/knowledgebase/{{knowledgebase_uuid}}"
    DELETE_KB = f"{BASE}/knowledgebase/{{knowledgebase_uuid}}"

    GET_DOCUMENTS = f"{BASE}/documents/"
    GET_DOCUMENT = f"{BASE}/document/{{document_uuid}}"
    POST_DOCUMENT = f"{BASE}/document/"
    PATCH_DOCUMENT = f"{BASE}/document/{{document_uuid}}"
    DELETE_DOCUMENT = f"{BASE}/document/{{document_uuid}}"

    GET_CONVERSATIONS = f"{BASE}/conversations/"
    GET_CONVERSATION = f"{BASE}/conversation/{{conversation_uuid}}"
    POST_CONVERSATION = f"{BASE}/conversation/"
    PATCH_CONVERSATION = f"{BASE}/conversation/{{conversation_uuid}}"
    DELETE_CONVERSATION = f"{BASE}/conversation/{{conversation_uuid}}"

    POST_LOAD_CONTROLLER = f"{BASE}/controllers/{{controller_uuid}}/load"
    POST_UNLOAD_CONTROLLER = f"{BASE}/controllers/{{controller_uuid}}/unload"

    POST_CONVERSATION_QUERY = f"{BASE}/conversation/{{conversation_uuid}}/query/{{query}}"
    POST_DIRECT_QUERY = f"{BASE}/controllers/{{controller_uuid}}/load"

    def __str__(self) -> str:
        """
        Getter method for a string representation.
        """
        return self.value


"""
Basic backend interaction
"""


@BACKEND.get(Endpoints.GET_STATUS)
async def get_status() -> dict:
    """
    Root endpoint for getting system status.
    :return: Response.
    """
    global STATUS
    return {"message": f"System is {'started' if STATUS else 'stopped'}!"}


@BACKEND.post(Endpoints.POST_START)
@access_validator(status=False)
async def post_start() -> dict:
    """
    Endpoint for starting system.
    :return: Response.
    """
    global STATUS
    STATUS = True
    return {"message": f"System started!"}


@BACKEND.post(Endpoints.POST_STOP)
@access_validator(status=True)
async def post_stop() -> dict:
    """
    Endpoint for stopping system.
    :return: Response.
    """
    global STATUS
    STARTED = False
    return {"message": f"System stopped!"}


"""
Controller
"""


"""
Backend runner
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
