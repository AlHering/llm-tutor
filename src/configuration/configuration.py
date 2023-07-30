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


"""
Environment file
"""
ENV = dotenv_values(os.path.join(PATHS.PACKAGE_PATH, ".env"))


"""
Logger
"""
LOGGER = logging.Logger("LLMTutor")


"""
FRONTENDS
"""
FLASK_CONFIG = flask_frontend_config.global_config
PATHS.FLASK_COMMON_STATIC = os.path.join(
    PATHS.SOURCE_PATH, "view", "flask_frontend", "common_static")
PATHS.FLASK_COMMON_TEMPLATES = os.path.join(
    PATHS.SOURCE_PATH, "view", "flask_frontend", "common_templates")
