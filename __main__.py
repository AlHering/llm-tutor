# -*- coding: utf-8 -*-
"""
****************************************************
*                    LLM Tutor                     *
*            (c) 2023 Alexander Hering             *
****************************************************
"""
import os
from src.configuration import configuration as cfg
from src.control.tutor_controller import TutorController
from src.view.app import run_app
import threading


def setup_backend() -> None:
    """
    Function for setting up backend.
    """
    tc = TutorController()
    


if __name__ == "__main__":
    #backend_thread = threading.Thread(target=setup_backend)
    #backend_thread.start()
    tc = TutorController()
    tc.load_general_llm(os.path.join(cfg.PATHS.TEXTGENERATION_MODEL_PATH, "orca_mini_7B-GGML/orca-mini-7b.ggmlv3.q4_1.bin"), "llm")
    tc.load_knowledge_base(os.path.join(cfg.PATHS.DATA_PATH, "testing", "chromadb"))
    # Corpus used: https://www.kaggle.com/datasets/sbhatti/news-articles-corpus
    #corpus_path = os.path.join(
    #    cfg.PATHS.DATA_PATH, "library", "sbhatti_news-articles-corpus")
    #tc.load_document_folder(corpus_path)
    run_app(tc)

