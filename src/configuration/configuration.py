# -*- coding: utf-8 -*-
"""
****************************************************
*                    LLM Tutor                     *
*            (c) 2023 Alexander Hering             *
****************************************************
"""
import os
import logging
from dotenv import dotenv_values
from . import paths as PATHS
from . import urls as URLS
from . import flask_frontend_config
from . import streamlit_frontend_config


"""
Environment file
"""
ENV = dotenv_values(os.path.join(PATHS.PACKAGE_PATH, ".env"))


"""
Logger
"""
LOGGER = logging.Logger("LLMTutor")


"""
BACKENDS
"""
BACKEND_HOST = ENV.get("BACKEND_HOST", "127.0.0.1")
BACKEND_PORT = ENV.get("BACKEND_PORT"), "7861"


"""
FRONTENDS
"""
FLASK_CONFIG = flask_frontend_config.global_config
PATHS.FLASK_COMMON_STATIC = os.path.join(
    PATHS.SOURCE_PATH, "view", "flask_frontend", "common_static")
PATHS.FLASK_COMMON_TEMPLATES = os.path.join(
    PATHS.SOURCE_PATH, "view", "flask_frontend", "common_templates")
STREAMLIT_CONFIG = streamlit_frontend_config.CONFIG

FLASK_CONFIG["streamlit_port"] = str(STREAMLIT_CONFIG["server"]["port"])
