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
from datetime import datetime as dt
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


def interface_function() -> Optional[Any]:
    """
    Validation decorator.
    :param func: Decorated function.
    :return: Error message if status is incorrect, else function return.
    """
    global CONTROLLER

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
            requested = dt.now()
            response = await func(*args, **kwargs)
            responded = dt.now()
            CONTROLLER.post_object(
                "log",
                request={
                    "function": func.__name__,
                    "args": args,
                    "kwargs": kwargs
                },
                response=response,
                requested=requested,
                responded=responded
            )
            return response
        return inner
    return wrapper


"""
Dataclasses
"""


"""
BACKEND ENDPOINTS
"""


class Endpoints(str, Enum):
    """
    String-based endpoint enum class.
    """
    BASE = "/api/v1"

    GET_LLMS = f"{BASE}/llms/"
    GET_KBS = f"{BASE}/kbs/"

    CREATE_KB = f"{BASE}/kbs/create"
    DELETE_KB = f"{BASE}/kbs/delete/{{kb_id}}"

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


@BACKEND.get(Endpoints.GET_LLMS)
@interface_function()
async def get_llms() -> dict:
    """
    Endpoint for getting LLMs.
    :return: Response.
    """
    global CONTROLLER
    return {"llms": CONTROLLER.get_objects_by_type("modelinstance")}


@BACKEND.get(Endpoints.GET_KBS)
@interface_function()
async def get_kbs() -> dict:
    """
    Endpoint for getting KBs.
    :return: Response.
    """
    global CONTROLLER
    return {"kbs": CONTROLLER.get_objects_by_type("knowledgebase")}


@BACKEND.post(Endpoints.CREATE_KB)
@interface_function()
async def post_kb(handler: str, persistant_directory: str,  metadata: dict, embedding_instance_id: int, implementation: str) -> str:
    """
    Method for creating knowledgebase.
    :param handler: Knowledgebase handler.
    :param persistant_directory: Knowledgebase persistant directory.
    :param metadata: Knowledgebase metadata.
    :param embedding_instance: Embedding instance ID.
    :param implementation: Knowledgebase implementation.
    :return: Response.
    """
    global CONTROLLER
    kb_id = CONTROLLER.post_object("knowledgebase", handler=handler,
                                   persistant_directory=persistant_directory, meta_data=metadata, implementation=implementation)
    CONTROLLER.register_knowledgebase(kb_id=kb_id, handler=handler,
                                      persistant_directory=persistant_directory, meta_data=metadata, implementation=implementation)
    return {"kb_id": kb_id}


@BACKEND.delete(Endpoints.DELETE_KB)
@interface_function()
async def delete_kb(kb_id: int) -> dict:
    """
    Endpoint for deleting KBs.
    :param kb_id: int: Knowledgebase ID.
    :return: Response.
    """
    global CONTROLLER
    CONTROLLER.delete_object("knowledgebase", kb_id)
    CONTROLLER.wipe_knowledgebase(str(kb_id))
    return {"kb_id": kb_id}


@BACKEND.post(Endpoints.UPLOAD_DOCUMENT)
@interface_function()
async def upload_document(kb_id: int, document_content: str, document_metadata: dict = None) -> dict:
    """
    Endpoint for uploading a document.
    :param kb_id: int: KB ID.
    :param document_content: Document content.
    :param document_metadata: Document metadata.
    :return: Response.
    """
    global CONTROLLER
    document_id = CONTROLLER.embed_document(
        kb_id, document_content, document_metadata)
    return {"document_id": document_id}


@BACKEND.delete(Endpoints.DELETE_DOCUMENT)
@interface_function()
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
@interface_function()
async def post_qa_query(llm_id: int, kb_id: int, query: str, include_sources: bool = True) -> dict:
    """
    Endpoint for posting document qa query.
        :param llm_id: LLM ID.
        :param kb_id: Knowledgebase ID.
        :param query: Query.
        :param include_sources: Flag declaring, whether to include sources.
        :return: Response.
        """
    global CONTROLLER
    response = CONTROLLER.forward_document_qa(
        llm_id, kb_id, query, include_sources)
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
