# -*- coding: utf-8 -*-
"""
****************************************************
*          Basic Language Model Backend            *
*            (c) 2023 Alexander Hering             *
****************************************************
"""
import uvicorn
from enum import Enum
from typing import Optional, Any
from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel
from functools import wraps
from src.configuration import configuration as cfg
from src.control.backend_controller import BackendController

"""
Backend control
"""
BACKEND = FastAPI(title="LLM Tutor Backend", version="0.1",
                  description="Backend for serving LLM Tutor services.")
CONTROLLER: BackendController = BackendController()


def access_validator() -> Optional[Any]:
    """
    Validation decorator.
    :param func: Decorated function.
    :return: Error message if status is incorrect, else function return.
    """

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
    path: str
    type: str
    loader: str


"""
BACKEND ENDPOINTS
"""


class Endpoints(str, Enum):
    """
    String-based endpoint enum class.
    """
    BASE = "/api/v1"

    GET_LLM_CONFIGS = f"{BASE}/llms/"
    GET_KB_CONFIGS = f"{BASE}/kbs/"

    SET_LLM_CONFIG = f"{BASE}/llms/{{llm_id}}"
    SET_KB_CONFIG = f"{BASE}/kbs/{{kb_id}}"

    CREATE_KB_CONFIG = f"{BASE}/kbs/create"
    DELETE_KB_CONFIG = f"{BASE}/kbs/delete/{{kb_id}}"

    UPLOAD_DOCUMENT = f"{BASE}/kbs/upload/{{kb_id}}"
    DELETE_DOCUMENT = f"{BASE}/kbs/delete_doc/{{doc_id}}"

    POST_QUERY = f"{BASE}/query"

    def __str__(self) -> str:
        """
        Getter method for a string representation.
        """
        return self.value


"""
Endpoints
"""


@BACKEND.get(Endpoints.GET_LLM_CONFIGS)
@access_validator()
async def get_llm_configs() -> dict:
    """
    Endpoint for getting LLM configs.
    :return: Response.
    """
    global CONTROLLER
    return {"llm_configs": CONTROLLER.get_objects("llm_config")}


@BACKEND.get(Endpoints.GET_LLM_CONFIGS)
@access_validator()
async def get_kb_configs() -> dict:
    """
    Endpoint for getting KB configs.
    :return: Response.
    """
    global CONTROLLER
    return {"kb_configs": CONTROLLER.get_objects("kb_config")}


@BACKEND.post(Endpoints.SET_LLM_CONFIGS)
@access_validator()
async def set_llm_config(config_id: int) -> dict:
    """
    Endpoint for setting active LLM config.
    :param config_id: int: Config ID.
    :return: Response.
    """
    global CONTROLLER
    status = CONTROLLER.set_active("llm_config", config_id)
    return {"successful": status}


@BACKEND.post(Endpoints.SET_LLM_CONFIGS)
@access_validator()
async def set_kb_config(config_id: int) -> dict:
    """
    Endpoint for setting active KB config.
    :param config_id: int: Config ID.
    :return: Response.
    """
    global CONTROLLER
    status = CONTROLLER.set_active("llm_config", config_id)
    return {"successful": status}


@BACKEND.post(Endpoints.CREATE_KB_CONFIG)
@access_validator()
async def post_kb_config(payload: dict) -> dict:
    """
    Endpoint for setting active KB config.
    :param payload: Config.
    :return: Response.
    """
    global CONTROLLER
    config_id = CONTROLLER.post_object("kb_config", config=payload)
    CONTROLLER.kb_controller.register_knowledgebase(payload)
    return {"config_id": config_id}


@BACKEND.delete(Endpoints.DELETE_KB_CONFIG)
@access_validator()
async def delete_kb_config(config_id: int) -> dict:
    """
    Endpoint for setting active KB config.
    :param config_id: int: Config ID.
    :return: Response.
    """
    global CONTROLLER
    config = CONTROLLER.get_object_by_id("kb_config", config_id)
    config_id = CONTROLLER.delete_object("kb_config", config_id)
    CONTROLLER.kb_controller.wipe_knowledgebase(config["name"])
    return {"config_id": config_id}


@BACKEND.post(Endpoints.UPLOAD_DOCUMENT)
@access_validator()
async def upload_document(config_id: int, document_content: str) -> dict:
    """
    Endpoint for uploading a document.
    :param config_id: int: Config ID of KB.
    :param document_content: Document content.
    :return: Response.
    """
    global CONTROLLER
    document_id = CONTROLLER.embed_document(config_id, document_content)
    return {"document_id": document_id}


@BACKEND.delete(Endpoints.DELETE_DOCUMENT)
@access_validator()
async def delete_document(document_id: int) -> dict:
    """
    Endpoint for deleting document.
    :param document_id: Document ID.
    :return: Response.
    """
    global CONTROLLER
    document_id = CONTROLLER.delete_document_embeddings(document_id)
    return {"document_id": document_id}


@BACKEND.post(Endpoints.POST_QUERY)
@access_validator()
async def post_query(query: str) -> dict:
    """
    Endpoint for posting query.
    :param query: Query.
    :return: Response.
    """
    global CONTROLLER
    response = CONTROLLER.post_query(query)
    return {"response": response}

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
