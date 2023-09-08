# -*- coding: utf-8 -*-
"""
****************************************************
*          Basic Language Model Backend            *
*            (c) 2023 Alexander Hering             *
****************************************************
"""
import os
import copy
from time import sleep
from typing import Any
from uuid import uuid4
import streamlit as st
from src.configuration import configuration as cfg
from src.model.knowledgebase_control.chromadb_knowledgebase import ChromaKnowledgeBase
from src.utility.bronze import streamlit_utility, json_utility
from src.utility.silver.file_system_utility import safely_create_path
import json
import requests


def change_kb_name() -> None:
    """
    Function for changing KB name.
    """
    st.session_state["CACHE"]["knowledgebases"][st.session_state["CACHE"]["knowledgebases"].index(
        st.session_state["CACHE"]["current_kb"])] = st.session_state["CACHE"]["change_kb_name"]
    st.session_state["CACHE"]["collections"][st.session_state["CACHE"]["change_kb_name"]] = st.session_state["CACHE"]["collections"].pop(
        st.session_state["CACHE"]["current_kb"])
    st.session_state["CACHE"]["current_kb"] = st.session_state["CACHE"]["change_kb_name"]
    json_utility.save(
        st.session_state["CACHE"], cfg.PATHS.MODEL_CONTROL_FRONTEND_CACHE)


def run_page() -> None:
    """
    Function for running the main page.
    """
    st.title("LLM Tutor")
    st.header("")

    if "KB" not in st.session_state:
        with st.spinner("Loading knowledgebase backend..."):
            st.session_state["KB"] = ChromaKnowledgeBase(
                os.path.join(cfg.PATHS.BACKEND_PATH, "chroma.db"))

    new_kb_button = st.sidebar.button("New Knowledgebase")
    if new_kb_button:
        new_uuid = str(uuid4())
        st.session_state["CACHE"]["knowledgebases"].append(new_uuid)
        st.session_state["CACHE"]["documents"][new_uuid] = {}
        st.session_state["CACHE"]["current_kb"] = new_uuid
        st.session_state["CACHE"]["collections"][new_uuid] = new_uuid
        st.session_state["KB"].get_or_create_collection(new_uuid)
        json_utility.save(
            st.session_state["CACHE"], cfg.PATHS.MODEL_CONTROL_FRONTEND_CACHE)

    st.session_state["CACHE"]["change_kb_name"] = st.sidebar.text_input(
        "Change Knowledgebase name", value=st.session_state["CACHE"]["current_kb"])
    if st.session_state["CACHE"]["change_kb_name"] != st.session_state["CACHE"]["current_kb"]:
        change_kb_name()

    save_cache_button = st.sidebar.button("Save state")
    if save_cache_button:
        json_utility.save(
            st.session_state["CACHE"], cfg.PATHS.MODEL_CONTROL_FRONTEND_CACHE)

    if st.session_state["CACHE"]["current_kb"] != "default":
        delete_kb = st.sidebar.button("Delete knowledgebase")
        if delete_kb:
            to_remove = st.session_state["CACHE"]["current_kb"]
            st.session_state["CACHE"]["current_kb"] = "default"
            st.session_state["CACHE"]["change_kb_name"] = "default"
            st.session_state["CACHE"]["knowledgebases"].remove(to_remove)
            st.session_state["CACHE"]["documents"].pop(to_remove)
            st.session_state["CACHE"]["collections"].pop(to_remove)
            json_utility.save(
                st.session_state["CACHE"], cfg.PATHS.MODEL_CONTROL_FRONTEND_CACHE)

    st.session_state["CACHE"]["current_kb"] = st.selectbox(
        "Knowledgebase",
        st.session_state["CACHE"]["knowledgebases"],
        st.session_state["CACHE"]["knowledgebases"].index(
            st.session_state["CACHE"]["current_kb"]),
        format_func=lambda x: x,
        placeholder="default"
    )


def run_app() -> None:
    """
    Main runner function.
    """
    st.set_page_config(
        page_title="LLM Tutor",
        page_icon=":books:"
    )
    if os.path.exists(cfg.PATHS.MODEL_CONTROL_FRONTEND_CACHE):
        st.session_state["CACHE"] = json_utility.load(
            cfg.PATHS.MODEL_CONTROL_FRONTEND_CACHE)
    else:
        st.session_state["CACHE"] = {
            "knowledgebases": ["default"],
            "documents": {
                "default": {}
            },
            "collections": {
                "default": "base"
            }
        }
        st.session_state["CACHE"]["current_kb"] = "default"
    safely_create_path(cfg.PATHS.MODEL_CONTROL_FRONTEND_ASSETS)
    run_page()


if __name__ == "__main__":
    run_app()
