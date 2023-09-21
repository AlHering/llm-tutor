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
from enum import Enum
from src.utility.bronze import time_utility
import os
from itertools import chain
from typing import List, Union
import requests
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


class BackendEndpoints(str, Enum):
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


def create_table(identifier: str, entries: List[dict]) -> str:
    """
    Function for creating an interactive table from a list of entries.
    :param identifier: Element identifier.
    :param entries: List of entries.
    :return: Table html.
    """
    columns = list(
        {f'\n<th scope="col">{key}</th>' for key in chain(*entries)})
    script_columns = list(
        {f"\n{{ data: '{key}' }}" for key in chain(*entries)})
    table_html = f"""
    <div class="container" style="width:60%;">
    <table id="example">
        <thead>
            <tr>
                {columns}
            </tr>
        </thead>
    </table>
    <script type="text/javascript" class="init">$(document).ready(function() {{
    // Create a new DataTable object
    table = $('#example').DataTable({{
        ajax: {{
            url: '/exampleData',
        }},
        columns: [
            {{ data: 'userId' }},
            {{ data: 'id' }},
            {{ data: 'title' }},
            {{ data: 'completed' }}
            ]
        }})
    }});</script>
    </div>
    """


def get_blueprints(global_config: dict) -> List[Blueprint]:
    """
    Main plugin handle function.
    :param global_config: Global Flask app config.
    :return: List of blueprints to integrate into flask app.
    """
    global_config["plugins"]["LLMTutor"] = {
        "kbs": requests.get(global_config["backend"]["api_base_url"]+BackendEndpoints.GET_KBS).json()["kbs"],
        "llms": requests.get(global_config["backend"]["api_base_url"]+BackendEndpoints.GET_LLMS).json()["llms"]
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
        if request.method == "GET":
            entries_columns = list({key for key in chain(
                *global_config["plugins"]["LLMTutor"]["kbs"])})
            print(entries_columns)
            fetching_columns = ",".join(
                [f"{{ data: '{key}' }}" for key in entries_columns])
            entries_fetching_script = """
            $(document).ready(function () {
                // Create a new DataTable object
                table = $('#kbs').DataTable({
                    ajax: {
                        url: '""" + global_config["backend"]["api_base_url"] + BackendEndpoints.GET_KBS + """',
                    },
                    columns: [""" + fetching_columns + """]
                })
            });
            """

        elif request.method == "POST":
            pass
        return render_template("knowledgebases.html", entries_columns=entries_columns, entries_fetching_script=entries_fetching_script, **global_config)

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
