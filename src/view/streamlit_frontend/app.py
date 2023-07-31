
# -*- coding: utf-8 -*-
"""
****************************************************
*                    LLM Tutor                     *
*            (c) 2023 Alexander Hering             *
****************************************************
"""
import os
from typing import Any
from uuid import uuid4
import streamlit as st
from src.configuration import configuration as cfg
from src.view.streamlit_frontend.chat_template import css, bot_template, user_template
from src.utility.bronze import streamlit_utility
from src.interfaces. streamlit_interface import start_controller_if_stopped, handle_request, BACKEND_ENDPOINTS
import json
import requests
from src.view.streamlit_frontend.pages import knowledgebase_app, model_app


def run_page() -> None:
    """
    Function for running "Home" page.
    """
    st.title("LLM Tutor")
    st.write(css, unsafe_allow_html=True)

    st.header("Upload, analyze and talk to learning material.")
    if "backend_controller_started" not in st.session_state:
        start_controller_if_stopped()
        st.session_state["backend_controller_started"] = True

    options = handle_request(
        "get", BACKEND_ENDPOINTS.GET_CONFIGS).get("configs", [])
    options.insert(0, "<< NEW >>")
    option = st.selectbox(
        'Choose a previously created Tutor:',
        options)
    if st.button("Load ..."):
        if option == "<< NEW >>":
            config_name = st.text_area("Choose Tutor name", f"{uuid4()}")
            if config_name in options:
                st.warning(f"'{config_name}' already existing!")
            else:
                if st.button("Create ..."):
                    st.session_state["tutor_config_name"] = config_name
        else:
            handle_request("post", BACKEND_ENDPOINTS.POST_LOAD_CONFIG, {
                "config_name": option})


PAGES = {
    "Home": run_page,
    "Knowledgebases": knowledgebase_app.run_page,
    "Models": model_app.run_page,
}


def run_app() -> None:
    """
    Function for running the app.
    """
    st.set_page_config(
        page_title="LLM Tutor",
        page_icon=":books:"
    )
    page = st.sidebar.selectbox(
        "Navigation",
        PAGES.keys()
    )
    PAGES[page]()


if __name__ == "__main__":
    run_app()
