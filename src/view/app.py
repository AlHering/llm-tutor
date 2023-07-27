
# -*- coding: utf-8 -*-
"""
****************************************************
*                    LLM Tutor                     *
*            (c) 2023 Alexander Hering             *
****************************************************
"""
import streamlit as st
from src.view.chat_template import css, bot_template, user_template


def handle_user_query(query):
    """
    Function for handling user query.
    :param query: User query.
    """
    pass


def handle_file_loading(file_paths, doc_type, splitting=None):
    """
    Function for handling document loading.
    :param file_paths: File paths.
    :param doc_type: Document type.
    """
    if doc_type not in st.session_state.controller.doc_types:
        st.session_state.controller.register_document_type(
            doc_type, splitting=splitting)
    st.session_state.controller.load_files(file_paths, doc_type)


def run_app(controller) -> None:
    """
    Function for running app.
    """
    st.session_state.controller = controller
    for doc_type in ["skript", "presentation", "book"]:
        controller.kb.get_or_create_collection(doc_type)

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
                        handle_file_loading(files[doc_type], doc_type)


if __name__ == "__main__":
    run_app()
