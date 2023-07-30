
# -*- coding: utf-8 -*-
"""
****************************************************
*                    LLM Tutor                     *
*            (c) 2023 Alexander Hering             *
****************************************************
"""
import os
from typing import Any
import streamlit as st
from src.configuration import configuration as cfg
from src.view.streamlit_frontend.chat_template import css, bot_template, user_template
from src.utility.bronze import streamlit_utility
from src.interfaces. streamlit_interface import start_controller_if_stopped, handle_request
import json
import requests


def run_app() -> None:
    """
    Function for running app.
    """
    st.set_page_config(
        page_title="LLM Tutor",
        page_icon=":books:"
    )
    st.title("Index")
    st.write(css, unsafe_allow_html=True)

    st.header("LLM Tutor: Upload and talk to learning material.")
    if "backend_controller_started" not in st.session_state:
        start_controller_if_stopped()
        st.session_state["backend_controller_started"] = True


if __name__ == "__main__":
    run_app()
