
# -*- coding: utf-8 -*-
"""
****************************************************
*                    LLM Tutor                     *
*            (c) 2023 Alexander Hering             *
****************************************************
"""
import os
import asyncio
import streamlit as st
from src.configuration import configuration as cfg
from src.view.chat_template import css, bot_template, user_template
from langchain.docstore.document import Document
import json
import requests


BACKEND_BASE_URL = "http://127.0.0.1:7861"


def handle_user_query(query):
    """
    Function for handling user query.
    :param query: User query.
    """
    pass


def handle_request(method: str, endpoint: str, data: dict = None):
    print(f"{method} :: {endpoint} :: {data}")
    try:
        response = {"get": requests.get, "post": requests.post}[
            method](f"{BACKEND_BASE_URL}{endpoint}", json=data)

    except requests.exceptions.SSLError:
        print("SSL Error")
        response = {"get": requests.get, "post": requests.post}[
            method](f"{BACKEND_BASE_URL}{endpoint}", json=data, verify=False)
    try:
        res = json.loads(response.content.decode('utf-8'))
    except json.decoder.JSONDecodeError:
        res = response.text
    print(res)
    return res


def run_app() -> None:
    """
    Function for running app.
    """
    resp = handle_request("get", "/")
    if resp["message"] == "System is stopped":
        resp = handle_request("post", "/start")
        print(resp)
        resp = handle_request("post", "/load_llm", {
            "model_path": os.path.join(cfg.PATHS.TEXTGENERATION_MODEL_PATH,
                                       "TheBloke_orca_mini_7B-GGML/orca-mini-7b.ggmlv3.q4_1.bin"),
            "model_type": "llm"
        })
        print(resp)
        resp = handle_request("post", "/load_kb")
        print(resp)

    st.set_page_config(
        page_title="LLM Tutor",
        page_icon=":books:"
    )
    st.write(css, unsafe_allow_html=True)

    st.header("LLM Tutor: Upload and talk to learning material.")
    st.text_input("Query:")

    st.write(user_template.replace("{{MSG}}", "Test"), unsafe_allow_html=True)
    st.write(bot_template.replace("{{MSG}}", "Test"), unsafe_allow_html=True)

    with st.sidebar:
        st.subheader("Learning Material")
        files = {
            "skripts": st.file_uploader("Skripts", accept_multiple_files=True),
            "presentations": st.file_uploader("Presentations", accept_multiple_files=True),
            "books": st.file_uploader("Books", accept_multiple_files=True)
        }
        if st.button("Load"):
            with st.spinner("Processing"):
                for doc_type in files:
                    if files[doc_type]:
                        resp = handle_request("post", "/embed", data={"documents":
                                                                      [{"page_content": f.read().decode("utf-8"), "metadata": {"file_name": f.name,
                                                                                                                               "file_size": f.size, "file_type": f.type}} for f in files[doc_type]]
                                                                      })
                        print(resp)
                        files[doc_type].clear()


if __name__ == "__main__":
    run_app()
