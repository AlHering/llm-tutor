# -*- coding: utf-8 -*-
"""
****************************************************
*                    LLM Tutor                     *
*            (c) 2023 Alexander Hering             *
****************************************************
"""
from sqlalchemy import MetaData, Table, Column, String, Boolean, Integer, JSON, Text, DateTime, CHAR, ForeignKey, Table, \
    Float, BLOB, TEXT, func, inspect, select, text
from sqlalchemy import and_, or_, not_
from sqlalchemy.ext.automap import automap_base, classname_for_table
from typing import Any, Union, List, Tuple, Optional
import copy
import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from src.configuration import configuration as cfg
from src.utility.bronze import dictionary_utility, sqlalchemy_utility, time_utility


CONTROLLER = {
    "__tablename__": "controller",
    "__table_args__": {"comment": "Controller Table."},
    "uuid": Column(String, primary_key=True, unique=True, nullable=False,
                   comment="UUID of the controller."),
    "language_model_uuid": Column(String, ForeignKey(f"model.uuid"),
                                  comment="Registered language model to use."),

    "knowledgebase_uuid": Column(String, ForeignKey(f"knowledgebase.uuid"),
                                 comment="Registered knowledgebase to use.")
}


MODEL = {
    "__tablename__": "model",
    "__table_args__": {"comment": "Model Table."},
    "uuid": Column(String, primary_key=True, unique=True, nullable=False,
                   comment="UUID of the model."),
    "path": Column(String, nullable=False,
                   comment="Path of the model."),
    "model_type": Column(String, nullable=False,
                         comment="Type of the model."),
    "model_loader": Column(String, nullable=False,
                           comment="Loader for the model.")
}

KNOWLEDGEBASE = {
    "__tablename__": "knowledgebase",
    "__table_args__": {"comment": "Knowledgebase Table."},
    "uuid": Column(String, primary_key=True, unique=True, nullable=False,
                   comment="UUID of the knowledgebase."),
    "path": Column(String, nullable=False,
                   comment="Path to the knowledgebase."),
    "loader": Column(String, nullable=False,
                     comment="Loader for knowledgebase."),
    "embedding_model_uuid": Column(String, ForeignKey(f"model.uuid"),
                                   comment="Registered embedding model to use."),
    "documents": relationship("Document", comment="Documents included in the knowledgebase.")

}

DOCUMENT = {
    "__tablename__": "document",
    "__table_args__": {"comment": "Document Table."},
    "uuid": Column(String, primary_key=True, unique=True, nullable=False,
                   comment="UUID of the document."),
    "content": Column(BLOB, comment="Content of the document."),
    "meta_data": Column(JSON, comment="Metadata of the document.")
}

CONVERSATION = {
    "__tablename__": "conversation",
    "__table_args__": {"comment": "Conversation Table."},
    "uuid": Column(String, primary_key=True, unique=True, nullable=False,
                   comment="UUID of the conversation."),
    "controller_uuid": Column(String, ForeignKey(f"model.uuid"),
                              comment="UUID of managing controller."),
    "conversation_content": Column(JSON, comment="Conversation content.")

}


def create_or_load_database(database_uri: str) -> dict:
    """
    Function for creating or loading backend database.
    :param database_uri: Database URI.
    """
    pass
