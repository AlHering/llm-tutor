# -*- coding: utf-8 -*-
"""
****************************************************
*        Share Screener Blueprints-Plugin
*            (c) 2023 Alexander Hering             *
****************************************************
"""
import os
from typing import List, Union
from flask import Blueprint, render_template, Response
import os


PLUGIN_PATH = os.path.dirname(os.path.abspath(__file__))
TICKERS = {}
STREAMLIT_BLUEPRINT = Blueprint(
    "streamlit",
    __name__,
    template_folder=f"{PLUGIN_PATH}/templates",
    static_folder=f"{PLUGIN_PATH}/static",
    url_prefix='/streamlit'
)


def get_blueprints(global_config: dict) -> List[Blueprint]:
    """
    Main plugin handle function.
    :param global_config: Global Flask app config.
    :return: List of blueprints to integrate into flask app.
    """
    global_config["plugins"]["SharesBlueprints"] = {
    }

    @STREAMLIT_BLUEPRINT.route("/tutor", methods=["GET", "POST"])
    def tutor() -> Union[str, Response]:
        """
        Share screener template method.
        :return: Share screener template.
        """
        return render_template("streamlit_index.html", **global_config)

    return [STREAMLIT_BLUEPRINT]


def get_menu() -> dict:
    """
    Function for getting menu dictionary.
    :return: Menu dictionary.
    """
    return {
        "Streamlit": {
            "Tutor": {
                "icon": "bed",
                "type": "fa",
                "href": "streamlit.tutor"
            }
        }
    }
