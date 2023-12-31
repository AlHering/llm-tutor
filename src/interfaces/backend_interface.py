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
from src.control.backend_controller import BackendController

"""
Backend control
"""
BACKEND = FastAPI(title="LLMTutor Backend", version="0.1",
                  description="LLM-powered backend for document embedding an querying.")
STATUS = False
CONTROLLER: BackendController = None


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
    uuid: str
    path: str
    type: str
    loader: str


class Knowledgebase(BaseModel):
    """
    Dataclass for knowledgebase representation.
    """
    uuid: str
    path: str
    loader: str
    embedding_model_uuid: str
    document_uuids: List[str]


class Document(BaseModel):
    """
    Dataclass for documents.
    """
    uuid: str
    content: str
    meta_data: dict


class Controller(BaseModel):
    """
    Dataclass for controller representation.
    """
    uuid: str
    language_model_uuid: str
    knowledgebase_uuid: str


class Conversation(BaseModel):
    """
    Dataclass for conversation representation.
    """
    uuid: str
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
Basic backend endpoints
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
    global CONTROLLER
    CONTROLLER = BackendController()
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
    global CONTROLLER
    CONTROLLER.shutdown()
    STATUS = False
    return {"message": f"System stopped!"}


"""
Controller endpoints
"""


@BACKEND.get(Endpoints.GET_CONTROLLERS)
@access_validator(status=True)
async def get_controllers() -> dict:
    """
    Endpoint for getting controllers.
    :return: Response.
    """
    global CONTROLLER
    return {"controllers": CONTROLLER.get_objects("controller")}


@BACKEND.get(Endpoints.GET_CONTROLLER)
@access_validator(status=True)
async def get_controller(controller_uuid: str) -> dict:
    """
    Endpoint for getting a specific controller.
    :param controller_uuid: Controller UUID.
    :return: Response.
    """
    global CONTROLLER
    return {"controller": CONTROLLER.get_object("controller", controller_uuid)}


@BACKEND.post(Endpoints.POST_CONTROLLER)
@access_validator(status=True)
async def post_controller(controller: Controller) -> dict:
    """
    Endpoint for posting a controller.
    :param controller: Controller.
    :return: Response.
    """
    return {"uuid": CONTROLLER.post_object("controller",
                                           **controller.dict())}


@BACKEND.patch(Endpoints.PATCH_CONTROLLER)
@access_validator(status=True)
async def patch_controller(controller_uuid: str, controller: Controller) -> dict:
    """
    Endpoint for patching a controller.
    :param controller_uuid: Controller UUID.
    :param controller: Controller.
    :return: Response.
    """
    return {"uuid": CONTROLLER.patch_object("controller",
                                            controller_uuid,
                                            **controller.dict())}


@BACKEND.delete(Endpoints.DELETE_CONTROLLER)
@access_validator(status=True)
async def delete_controller(controller_uuid: str) -> dict:
    """
    Endpoint for deleting a controller.
    :param controller_uuid: Controller UUID.
    :return: Response.
    """
    return {"uuid": CONTROLLER.delete_object("controller",
                                             controller_uuid)}


@BACKEND.post(Endpoints.POST_LOAD_CONTROLLER)
@access_validator(status=True)
async def post_load_controller(controller_uuid: str) -> dict:
    """
    Endpoint for loading a controller.
    :param controller_uuid: Controller UUID.
    :return: Response.
    """
    return {}


@BACKEND.post(Endpoints.POST_UNLOAD_CONTROLLER)
@access_validator(status=True)
async def post_unload_controller(controller_uuid: str) -> dict:
    """
    Endpoint for unloading a controller.
    :param controller_uuid: Controller UUID.
    :return: Response.
    """
    return {}


@BACKEND.post(Endpoints.POST_DIRECT_QUERY)
@access_validator(status=True)
async def post_direct_query(controller_uuid: str, query: str) -> dict:
    """
    Endpoint for posting a query to a controller.
    :param controller_uuid: Controller UUID.
    :param query: Query to forward.
    :return: Response.
    """
    return {}


"""
Models endpoints
"""


@BACKEND.get(Endpoints.GET_MODELS)
@access_validator(status=True)
async def get_models() -> dict:
    """
    Endpoint for getting models.
    :return: Response.
    """
    global CONTROLLER
    return {"models": CONTROLLER.get_objects("model")}


@BACKEND.get(Endpoints.GET_MODEL)
@access_validator(status=True)
async def get_model(model_uuid: str) -> dict:
    """
    Endpoint for getting a specific model.
    :param model_uuid: Model UUID.
    :return: Response.
    """
    global CONTROLLER
    return {"models": CONTROLLER.get_object("model", model_uuid)}


@BACKEND.post(Endpoints.POST_MODEL)
@access_validator(status=True)
async def post_model(model: Model) -> dict:
    """
    Endpoint for posting a model.
    :param model: Model.
    :return: Response.
    """
    return {"uuid": CONTROLLER.post_object("model",
                                           **model.dict())}


@BACKEND.patch(Endpoints.PATCH_MODEL)
@access_validator(status=True)
async def patch_model(model_uuid: str, model: Model) -> dict:
    """
    Endpoint for patching a model.
    :param model_uuid: Model UUID.
    :param model: Model.
    :return: Response.
    """
    return {"uuid": CONTROLLER.patch_object("model",
                                            model_uuid,
                                            **model.dict())}


@BACKEND.delete(Endpoints.DELETE_MODEL)
@access_validator(status=True)
async def delete_model(model_uuid: str) -> dict:
    """
    Endpoint for deleting a model.
    :param model_uuid: Model UUID.
    :return: Response.
    """
    return {"uuid": CONTROLLER.delete_object("model",
                                             model_uuid)}


"""
Knowledgebases endpoints
"""


@BACKEND.get(Endpoints.GET_KBS)
@access_validator(status=True)
async def get_knowledgebases() -> dict:
    """
    Endpoint for getting knowledgebases.
    :return: Response.
    """
    global CONTROLLER
    return {"knowledgebases": CONTROLLER.get_objects("knowledgebase")}


@BACKEND.get(Endpoints.GET_KB)
@access_validator(status=True)
async def get_knowledgebase(knowledgebase_uuid: str) -> dict:
    """
    Endpoint for getting a specific knowledgebase.
    :param knowledgebase_uuid: Knowledgebase UUID.
    :return: Response.
    """
    global CONTROLLER
    return {"knowledgebase": CONTROLLER.get_object("knowledgebase", knowledgebase_uuid)}


@BACKEND.post(Endpoints.POST_KB)
@access_validator(status=True)
async def post_knowledgebase(knowledgebase: Knowledgebase) -> dict:
    """
    Endpoint for posting a knowledgebase.
    :param knowledgebase: Knowledgebase.
    :return: Response.
    """
    return {"uuid": CONTROLLER.post_object("knowledgebase",
                                           **knowledgebase.dict())}


@BACKEND.patch(Endpoints.PATCH_KB)
@access_validator(status=True)
async def patch_knowledgebase(knowledgebase_uuid: str, knowledgebase: Knowledgebase) -> dict:
    """
    Endpoint for patching a knowledgebase.
    :param knowledgebase_uuid: Knowledgebase UUID.
    :param knowledgebase: Knowledgebase.
    :return: Response.
    """
    return {"uuid": CONTROLLER.patch_object("knowledgebase",
                                            knowledgebase_uuid,
                                            **knowledgebase.dict())}


@BACKEND.delete(Endpoints.DELETE_KB)
@access_validator(status=True)
async def delete_knowledgebase(knowledgebase_uuid: str) -> dict:
    """
    Endpoint for deleting a knowledgebase.
    :param knowledgebase_uuid: Knowledgebase UUID.
    :return: Response.
    """
    return {"uuid": CONTROLLER.delete_object("knowledgebase",
                                             knowledgebase_uuid)}


"""
Document endpoints
"""


@BACKEND.get(Endpoints.GET_DOCUMENTS)
@access_validator(status=True)
async def get_documents() -> dict:
    """
    Endpoint for getting documents.
    :return: Response.
    """
    global CONTROLLER
    return {"documents": CONTROLLER.get_objects("document")}


@BACKEND.get(Endpoints.GET_DOCUMENT)
@access_validator(status=True)
async def get_document(document_uuid: str) -> dict:
    """
    Endpoint for getting a specific document.
    :param document_uuid: Document UUID.
    :return: Response.
    """
    global CONTROLLER
    return {"document": CONTROLLER.get_object("document", document_uuid)}


@BACKEND.post(Endpoints.POST_DOCUMENT)
@access_validator(status=True)
async def post_document(document: Document) -> dict:
    """
    Endpoint for posting a document.
    :param document: Document.
    :return: Response.
    """
    return {"uuid": CONTROLLER.post_object("documet",
                                           **document.dict())}


@BACKEND.patch(Endpoints.PATCH_DOCUMENT)
@access_validator(status=True)
async def patch_document(document_uuid: str, document: Document) -> dict:
    """
    Endpoint for patching a document.
    :param document_uuid: Document UUID.
    :param document: Document.
    :return: Response.
    """
    return {"uuid": CONTROLLER.patch_object("document",
                                            document_uuid,
                                            **document.dict())}


@BACKEND.delete(Endpoints.DELETE_DOCUMENT)
@access_validator(status=True)
async def delete_document(document_uuid: str) -> dict:
    """
    Endpoint for deleting a document.
    :param document_uuid: Document UUID.
    :return: Response.
    """
    return {"uuid": CONTROLLER.delete_object("document",
                                             document_uuid)}


"""
Conversation endpoints
"""


@BACKEND.get(Endpoints.GET_CONVERSATIONS)
@access_validator(status=True)
async def get_conversations() -> dict:
    """
    Endpoint for getting conversations.
    :return: Response.
    """
    global CONTROLLER
    return {"conversations": CONTROLLER.get_objects("conversation")}


@BACKEND.get(Endpoints.GET_CONVERSATION)
@access_validator(status=True)
async def get_conversation(conversation_uuid: str) -> dict:
    """
    Endpoint for getting a specific conversation.
    :param conversation_uuid: Conversation UUID.
    :return: Response.
    """
    global CONTROLLER
    return {"conversation": CONTROLLER.get_object("conversation", conversation_uuid)}


@BACKEND.post(Endpoints.POST_CONVERSATION)
@access_validator(status=True)
async def post_conversation(conversation: Conversation) -> dict:
    """
    Endpoint for posting a conversation.
    :param conversation: Conversation.
    :return: Response.
    """
    return {"uuid": CONTROLLER.post_object("conversation",
                                           **conversation.dict())}


@BACKEND.patch(Endpoints.PATCH_CONVERSATION)
@access_validator(status=True)
async def patch_conversation(conversation_uuid: str, conversation: Conversation) -> dict:
    """
    Endpoint for patching a conversation.
    :param conversation_uuid: Conversation UUID.
    :param conversation: Conversation.
    :return: Response.
    """
    return {"uuid": CONTROLLER.patch_object("conversation",
                                            conversation_uuid,
                                            **conversation.dict())}


@BACKEND.delete(Endpoints.DELETE_CONVERSATION)
@access_validator(status=True)
async def delete_conversation(conversation_uuid: str) -> dict:
    """
    Endpoint for deleting a conversation.
    :param conversation_uuid: Conversation UUID.
    :return: Response.
    """
    return {"uuid": CONTROLLER.delete_object("conversation",
                                             conversation_uuid)}


@BACKEND.post(Endpoints.POST_CONVERSATION_QUERY)
@access_validator(status=True)
async def post_conversation_query(conversation_uuid: str, query: str) -> dict:
    """
    Endpoint for posting a conversation query.
    :param conversation_uuid: Conversation UUID.
    :param query: Query to forward.
    :return: Response.
    """
    return {}


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
