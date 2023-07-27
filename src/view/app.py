
# -*- coding: utf-8 -*-
"""
****************************************************
*                    LLM Tutor                     *
*            (c) 2023 Alexander Hering             *
****************************************************
"""
import streamlit as st



def run_app() -> None:
    """
    Function for running app.
    """
    st.set_page_config(
        page_title="LLM Tutor",
        page_icon=":books:"
    )

    st.header("LLM Tutor: Upload and talk to learning material.")
    st.text_input("Query:")

    with st.sidebar:
        st.subheader("Learning Material")
        st.file_uploader("Skripts")
        st.file_uploader("Presentations")
        st.file_uploader("Books")