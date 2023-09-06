# -*- coding: utf-8 -*-
"""
****************************************************
*          Basic Language Model Backend            *
*            (c) 2023 Alexander Hering             *
****************************************************
"""
import unittest
import gc
import os
import shutil
from datetime import datetime
from typing import Any
from src.configuration import configuration as cfg
from src.control.backend_controller import BackendController, sqlalchemy_utility


TESTING_DB_PATH = f"{cfg.PATHS.TEST_PATH}/DataModelTest/backend.db"


class DataModelTest(unittest.TestCase):
    """
    Test case class for testing the data model.
    """

    def test_01_infrastructure(self) -> None:
        """
        Method for testing basic infrastructure.
        """
        self.assertTrue(os.path.exists(TESTING_DB_PATH))
        self.assertTrue(all(hasattr(self.controller, attribute) for attribute in [
                        "base", "engine", "model", "session_factory", "primary_keys"]))
        self.assertEqual(len(
            [c for c in self.controller.base.metadata.tables[f"{self.schema}llm_config"].columns]), len(self.llm_config_columns))
        self.assertEqual(len(
            [c for c in self.controller.base.metadata.tables[f"{self.schema}kb_config"].columns]), len(self.kb_config_columns))
        self.assertEqual(len(
            [c for c in self.controller.base.metadata.tables[f"{self.schema}document"].columns]), len(self.document_columns))
        self.assertEqual(len(
            [c for c in self.controller.base.metadata.tables[f"{self.schema}log"].columns]), len(self.log_columns))

    def test_02_key_constraints(self) -> None:
        """
        Method for testing key constraints.
        """
        self.assertEqual(
            list(self.controller.base.metadata.tables[f"{self.schema}llm_config"].primary_key.columns)[0].name, "id")
        self.assertTrue(
            isinstance(list(self.controller.base.metadata.tables[f"{self.schema}llm_config"].primary_key.columns)[0].type, sqlalchemy_utility.Integer))
        self.assertEqual(
            list(self.controller.base.metadata.tables[f"{self.schema}kb_config"].primary_key.columns)[0].name, "id")
        self.assertTrue(
            isinstance(list(self.controller.base.metadata.tables[f"{self.schema}kb_config"].primary_key.columns)[0].type, sqlalchemy_utility.Integer))
        self.assertEqual(
            list(self.controller.base.metadata.tables[f"{self.schema}document"].primary_key.columns)[0].name, "id")
        self.assertTrue(
            isinstance(list(self.controller.base.metadata.tables[f"{self.schema}document"].primary_key.columns)[0].type, sqlalchemy_utility.Integer))
        self.assertEqual(
            list(self.controller.base.metadata.tables[f"{self.schema}log"].primary_key.columns)[0].name, "id")
        self.assertTrue(
            isinstance(list(self.controller.base.metadata.tables[f"{self.schema}log"].primary_key.columns)[0].type, sqlalchemy_utility.Integer))
        self.assertEqual(list(self.controller.base.metadata.tables[f"{self.schema}document"].foreign_keys)[
            0].column.table.name, f"{self.schema}kb_config")
        self.assertEqual(list(self.controller.base.metadata.tables[f"{self.schema}document"].foreign_keys)[
            0].target_fullname, f"{self.schema}kb_config.id")

    def test_03_model_key_representation(self) -> None:
        """
        Method for testing model representation.
        """
        primary_keys = {
            object_class: self.controller.model[object_class].__mapper__.primary_key[0].name for object_class in self.controller.model}
        self.assertEqual(primary_keys["llm_config"], "id")
        self.assertEqual(primary_keys["kb_config"], "id")
        self.assertEqual(primary_keys["document"], "id")
        self.assertEqual(primary_keys["log"], "id")

    def test_04_model_object_interaction(self) -> None:
        """
        Method for testing model representation.
        """
        kb_config = self.controller.model["kb_config"](
            **self.example_kb_config_data
        )
        self.assertTrue(all(hasattr(kb_config, attribute)
                        for attribute in self.kb_config_columns))

        document = self.controller.model["document"](
            **self.example_document_data
        )
        self.assertTrue(all(hasattr(document, attribute)
                        for attribute in self.document_columns))

        log = self.controller.model["log"](
            **self.example_log_data
        )
        self.assertTrue(all(hasattr(log, attribute)
                        for attribute in self.log_columns))

        kb_config_id = None
        with self.controller.session_factory() as session:
            session.add(kb_config)
            session.commit()
            kb_config_id = kb_config.id
        self.assertFalse(kb_config_id is None)

        with self.controller.session_factory() as session:
            resulting_kb_config = session.query(self.controller.model["kb_config"]).filter(
                getattr(self.controller.model["kb_config"], "id") == kb_config_id).first()
        self.assertFalse(resulting_kb_config is None)

        self.assertTrue(isinstance(resulting_kb_config.created,
                        datetime))
        with self.controller.session_factory() as session:
            resulting_kb_config = session.query(self.controller.model["kb_config"]).filter(
                getattr(self.controller.model["kb_config"], "id") == kb_config_id).first()
            resulting_kb_config.config = {"new_key": "new_val"}
            session.commit()
            session.refresh(resulting_kb_config)
        self.assertEqual(str(resulting_kb_config.config),
                         str({"new_key": "new_val"}))

        document.kb_config_id = kb_config_id
        with self.controller.session_factory() as session:
            session.add(document)
            session.commit()
            session.refresh(document)
            resulting_kb_config = session.query(self.controller.model["kb_config"]).filter(
                getattr(self.controller.model["kb_config"], "id") == kb_config_id).first()
            self.assertEqual(document.kb_config_id, resulting_kb_config.id)
            self.assertTrue(isinstance(
                document.kb_config, self.controller.model["kb_config"]))

    @classmethod
    def setUpClass(cls):
        """
        Class method for setting up test case.
        """
        if not os.path.exists(f"{cfg.PATHS.TEST_PATH}/DataModelTest"):
            os.makedirs(f"{cfg.PATHS.TEST_PATH}/DataModelTest")
        cls.controller = BackendController(
            database_uri=f"sqlite:///{TESTING_DB_PATH}")
        cls.schema = cls.controller.schema

        cls.example_llm_config_data = {
            "config": {"key": "val"}
        }
        cls.example_kb_config_data = {
            "config": {"key": "val"}
        }
        cls.example_document_data = {
            "content": "Document content."
        }
        cls.example_log_data = {"request":
                                {"my_request_key": "my_request_value"}}
        cls.llm_config_columns = ["id", "config",
                                  "created", "updated", "inactive"]
        cls.kb_config_columns = ["id", "config",
                                 "created", "updated", "inactive"]
        cls.document_columns = ["id", "content", "created",
                                "updated", "inactive", "kb_config_id"]
        cls.log_columns = ["id", "request",
                           "response", "requested", "responded"]

    @classmethod
    def tearDownClass(cls):
        """
        Class method for setting tearing down test case.
        """
        del cls.controller
        del cls.schema
        del cls.example_llm_config_data
        del cls.example_kb_config_data
        del cls.example_log_data
        del cls.example_document_data

        del cls.llm_config_columns
        del cls.kb_config_columns
        del cls.document_columns
        del cls.log_columns
        if os.path.exists(cfg.PATHS.TEST_PATH):
            shutil.rmtree(cfg.PATHS.TEST_PATH, ignore_errors=True)
        gc.collect()

    @classmethod
    def setup_class(cls):
        """
        Alternative class method for setting up test case.
        """
        cls.setUpClass()

    @classmethod
    def teardown_class(cls):
        """
        Alternative class for setting tearing down test case.
        """
        cls.tearDownClass()


if __name__ == '__main__':
    unittest.main()
