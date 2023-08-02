
# -*- coding: utf-8 -*-
"""
****************************************************
*                    LLM Tutor                     *
*            (c) 2023 Alexander Hering             *
****************************************************
"""
import os
from typing import Any
from time import sleep
import streamlit as st
from src.configuration import configuration as cfg
from src.utility.bronze import streamlit_utility
from src.view.streamlit_frontend.chat_template import css, bot_template, user_template
from src.interfaces. streamlit_interface import handle_request
import json
import requests


def run_page() -> None:
    """
    Function for running page.
    """
    st.title("Knowledgebases")
    st.write(css, unsafe_allow_html=True)

    st.header("Knowlegebase Control")

    streamlit_utility.wait_for_state_variable(
        streamlit_context=st, variable_name="backend_controller_started", waiting_message="Waiting for controller setup...")
