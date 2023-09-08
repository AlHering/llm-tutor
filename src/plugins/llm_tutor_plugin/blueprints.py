# -*- coding: utf-8 -*-
"""
****************************************************
*            ML Models Blueprints-Plugin
*            (c) 2023 Alexander Hering             *
****************************************************
"""
"""
Local imports - later to be implemented via FastAPI
"""
from src.utility.bronze import time_utility
import os
from typing import List, Union
from flask import Blueprint, render_template, Response, Request, request
import numpy as np
import os
PLUGIN_PATH = os.path.dirname(os.path.abspath(__file__))
TICKERS = {}
MODEL_CONTROL_BLUEPRINT = Blueprint(
    "llm_tutor",
    __name__,
    template_folder=f"{PLUGIN_PATH}/templates",
    static_folder=f"{PLUGIN_PATH}/static",
    url_prefix='/llm_tutor'
)


def get_blueprints(global_config: dict) -> List[Blueprint]:
    """
    Main plugin handle function.
    :param global_config: Global Flask app config.
    :return: List of blueprints to integrate into flask app.
    """
    global_config["plugins"]["LLMTutor"] = {
    }

    @MODEL_CONTROL_BLUEPRINT.route("/chat", methods=["GET", "POST"])
    def chat() -> Union[str, Response]:
        """
        LLM Tutor chat page endpoint method.
        :return: Rendered models page template.
        """
        ts = time_utility.get_timestamp_by_format("%d. %b. %Y (%H:%M:%S)")
        if request.method == "GET":
            if "chat" not in global_config:
                global_config["chat"] = [
                    {"user": "bot", "time": ts,
                        "text": "Hi, I am a bot. How are you. I can help you with your work!. Just ask me anything."}
                ]
        elif request.method == "POST":
            message = request.form.get("message")
            global_config["chat"].append({
                "user": "user",
                "time": ts,
                "text": message
            })
        return render_template("chat.html", **global_config)

    @MODEL_CONTROL_BLUEPRINT.route("/knowledgebases", methods=["GET", "POST"])
    def knowledgebases() -> Union[str, Response]:
        """
        LLM Tutor knowledgebase page endpoint method.
        :return: Rendered models page template.
        """
        ts = time_utility.get_timestamp()
        if request.method == "GET":
            if "chat" not in global_config:
                global_config["chat"] = [
                    {"user": "bot", "time": ts,
                        "text": "Hi, I am a bot. How are you. I can help you with your work!. Just ask me anything."}
                ]
        elif request.method == "POST":
            message = request.form.get("message")
            global_config["chat"].append({
                "user": "bot",
                "time": ts,
                "text": message
            })
        return render_template("knowledgebases.html", **global_config)

    @MODEL_CONTROL_BLUEPRINT.route("/llm_instances", methods=["GET", "POST"])
    def llm_instances() -> Union[str, Response]:
        """
        LLM Tutor LLM instances page endpoint method.
        :return: Rendered models page template.
        """
        ts = time_utility.get_timestamp()
        if request.method == "GET":
            if "chat" not in global_config:
                global_config["chat"] = [
                    {"user": "bot", "time": ts,
                        "text": "Hi, I am a bot. How are you. I can help you with your work!. Just ask me anything."}
                ]
        elif request.method == "POST":
            message = request.form.get("message")
            global_config["chat"].append({
                "user": "bot",
                "time": ts,
                "text": message
            })
        return render_template("llm_instances.html", **global_config)

    return [MODEL_CONTROL_BLUEPRINT]


def get_menu() -> dict:
    """
    Function for getting menu dictionary.
    :return: Menu dictionary.
    """
    return {
        "LLM Tutor": {
            "Chat": {
                "icon": "bed",
                "type": "fa",
                "href": "llm_tutor.chat"
            },
            "Knowledgebases": {
                "icon": "bed",
                "type": "fa",
                "href": "llm_tutor.knowledgebases"
            },
            "LLM Instances": {
                "icon": "bed",
                "type": "fa",
                "href": "llm_tutor.llm_instances"
            }
        }
    }
