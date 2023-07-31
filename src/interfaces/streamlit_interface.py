# -*- coding: utf-8 -*-
"""
****************************************************
*                    LLM Tutor                     *
*            (c) 2023 Alexander Hering             *
****************************************************
"""
import json
import requests
from typing import Any
from src.interfaces.backend_interface import Endpoints
from src.configuration import configuration as cfg


BACKEND_BASE_URL = f"http://{cfg.BACKEND_HOST}:{cfg.BACKEND_PORT}"
BACKEND_ENDPOINTS = Endpoints


def start_controller_if_stopped() -> None:
    """
    Function for checking and starting controller if stopped.
    """
    resp = handle_request("get", "/")
    if resp["message"] == "System is stopped":
        resp = handle_request("post", "/start")
        cfg.LOGGER.info(f"[Streamlit] Controller started: {resp}")


def handle_user_question(question: str) -> str:
    """
    Function for handling user question.
    :param query: User question.
    :return: Answer.
    """
    pass


def handle_user_conversation(conversation_uuid: str, question: str) -> dict:
    """
    Function for handling user conversation.
    :param conversation_uuid: Conversation UUID.
    :param question: User question.
    :return: Conversation result.
    """
    pass


def handle_request(method: str, endpoint: str, data: dict = None) -> Any:
    """
    Function for handling requests.
    :param method: Request method ("get", "post").
    :param endpoint: Endpoint to send request to.
    :param data: JSON data to include in request. Defaults to None.
    :return: Extracted response content.
    """
    try:
        response = {"get": requests.get, "post": requests.post}[
            method](f"{BACKEND_BASE_URL}{endpoint}", json=data)

    except requests.exceptions.SSLError:
        response = {"get": requests.get, "post": requests.post}[
            method](f"{BACKEND_BASE_URL}{endpoint}", json=data, verify=False)
    try:
        res = json.loads(response.content.decode('utf-8'))
    except json.decoder.JSONDecodeError:
        res = response.text
    return res
