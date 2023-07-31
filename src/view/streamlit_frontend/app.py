
# -*- coding: utf-8 -*-
"""
****************************************************
*                    LLM Tutor                     *
*            (c) 2023 Alexander Hering             *
****************************************************
"""
import os
from time import sleep
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


def choose_config() -> None:
    """
    Callback function for choosing config.
    """
    handle_request(
        "post", BACKEND_ENDPOINTS.POST_LOAD_CONFIG,  {"config_name": st.session_state["tutor_config_name"]}, as_params=True)


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

    new_option = st.text_input(
        "Create a new Tutor:", placeholder="Tutor Name")
    if new_option:
        handle_request("post", BACKEND_ENDPOINTS.POST_SAVE_CONFIG, {
            "config_name": new_option}, as_params=True)
        st.session_state["tutor_config_options"].insert(0, new_option)
        st.session_state["tutor_config_name"] = new_option
        choose_config()

    st.session_state["tutor_config_name"] = st.selectbox(
        'Choose a Tutor:',
        st.session_state["tutor_config_options"], on_change=choose_config)


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

    start_controller_if_stopped()
    st.session_state["tutor_config_name"] = None
    st.session_state["kb_config_name"] = None
    st.session_state["llm_config_name"] = None
    st.session_state["tutor_config_options"] = handle_request(
        "get", BACKEND_ENDPOINTS.GET_CONFIGS).get("configs", [])

    page = st.sidebar.selectbox(
        "Navigation",
        PAGES.keys()
    )
    if st.session_state["tutor_config_name"] is not None:
        with st.sidebar.expander(
            f"Profile: {st.session_state['tutor_config_name']}"
        ):
            st.write(st.session_state["kb_config_name"])

    PAGES[page]()


if __name__ == "__main__":
    run_app()
