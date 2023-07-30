# -*- coding: utf-8 -*-
"""
****************************************************
*                    LLM Tutor                     *
*            (c) 2023 Alexander Hering             *
****************************************************
"""
import os
from src.control.flask_frontend_controller import FlaskFrontendController
from src.configuration import configuration as cfg


if __name__ == "__main__":
    aura_app_controller = FlaskFrontendController(cfg.FLASK_CONFIG)
    aura_app_controller.run_app()
