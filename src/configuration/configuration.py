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
Backends
"""
BACKEND_HOST = ENV.get("BACKEND_HOST", "127.0.0.1")
BACKEND_PORT = ENV.get("BACKEND_PORT", "7861")


"""
Frontends
"""
FLASK_CONFIG = flask_frontend_config.global_config
STREAMLIT_CONFIG = streamlit_frontend_config.CONFIG
FLASK_CONFIG["streamlit_port"] = str(STREAMLIT_CONFIG["server"]["port"])
