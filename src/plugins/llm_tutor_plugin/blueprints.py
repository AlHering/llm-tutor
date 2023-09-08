# -*- coding: utf-8 -*-
"""
****************************************************
*            ML Models Blueprints-Plugin
*            (c) 2023 Alexander Hering             *
****************************************************
"""
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

    @MODEL_CONTROL_BLUEPRINT.route("/llm_tutor", methods=["GET", "POST"])
    def llm_tutor() -> Union[str, Response]:
        """
        LLM Tutor page endpoint method.
        :return: Rendered models page template.
        """
        global_config["chat"] = [
            {"user": "bot", "time": "12:45",
                "text": "Hi, I am a bot. How are you. I can help you with your work!. Just ask me anything."},
            {"user": "user", "time": "12:50",
                "text": "Hi, bot. I am a user. I am trying to learn something. Please help me with it."}
        ]
        return render_template("llm_tutor.html", **global_config)

    return [MODEL_CONTROL_BLUEPRINT]


def get_menu() -> dict:
    """
    Function for getting menu dictionary.
    :return: Menu dictionary.
    """
    return {
        "LLM Tutor": {
            "LLM Tutor": {
                "icon": "bed",
                "type": "fa",
                "href": "llm_tutor.llm_tutor"
            },
            "Knowledgebases": {
                "icon": "bed",
                "type": "fa",
                "href": "llm_tutor.llm_tutor"
            },
            "LLM Instances": {
                "icon": "bed",
                "type": "fa",
                "href": "llm_tutor.llm_tutor"
            }
        }
    }
