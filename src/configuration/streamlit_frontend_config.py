# -*- coding: utf-8 -*-
"""
****************************************************
*                    LLM Tutor                     *
*            (c) 2023 Alexander Hering             *
****************************************************
"""
import os
import toml

TOML_PATH = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(
    os.path.dirname(__file__))), "config.toml"))
CONFIG = toml.load(TOML_PATH)
