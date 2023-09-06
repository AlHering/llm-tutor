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
from src.control.backend_controller import BackendController, UUID
from src.model.backend_control.llm_pool import LLMPool
from src.configuration import configuration as cfg

TESTING_DB_PATH = f"{cfg.PATHS.TEST_PATH}/BackendControllerTest/backend.db"


class BackendControllerTest(unittest.TestCase):
    """
    Test case class for testing the backend controller.
    """

    def test_01_initiation_process(self):
        """
        Method for testing controller instantiation.
        """
        self.assertTrue(os.path.exists(TESTING_DB_PATH))
        self.assertTrue(all(getattr(self.controller, attribute) is not None for attribute in [
                        "base", "engine", "model", "session_factory", "primary_keys", "_cache", "llm_pool"]))
        self.assertTrue(isinstance(self.controller.llm_pool, LLMPool))

    def test_02_object_handling(self):
        """
        Method for testing object handling.
        """
        llm_config_id = self.controller.post_object(
            "llm_config", **self.example_llm_config_data)
        self.assertTrue(isinstance(llm_config_id, int))
        self.assertEqual(llm_config_id, 1)
        registered_llm_configs = self.controller.get_objects_by_type(
            "llm_config")
        self.assertEqual(len(registered_llm_configs), 1)
        self.assertEqual(registered_llm_configs[0].id, llm_config_id)
        self.assertEqual(
            str(registered_llm_configs[0].config), str(self.example_llm_config_data["config"]))
        self.controller.patch_object(
            "llm_config", llm_config_id, **self.example_llm_config_patch)
        patched_llm_config_object = self.controller.get_object_by_id(
            "llm_config", llm_config_id)
        for key in self.example_llm_config_patch:
            self.assertEqual(str(getattr(patched_llm_config_object, key)),
                             str(self.example_llm_config_patch[key]))

        kb_config_id = self.controller.post_object(
            "kb_config", **self.example_kb_config_data)
        registered_kb_configs = self.controller.get_objects_by_type(
            "kb_config")
        self.assertTrue(isinstance(kb_config_id, int))
        self.assertEqual(len(registered_kb_configs), 1)
        self.assertEqual(registered_kb_configs[0].id, kb_config_id)

        self.controller.delete_object("llm_config", llm_config_id)
        self.controller.delete_object("kb_config", kb_config_id)
        self.assertEqual(
            len(self.controller.get_objects_by_type("llm_config")), 0)
        self.assertEqual(
            len(self.controller.get_objects_by_type("kb_config")), 0)

    def test_03_llm_handling(self):
        """
        Method for testing LLM handling.
        """
        pass

    @classmethod
    def setUpClass(cls):
        """
        Class method for setting up test case.
        """
        if not os.path.exists(f"{cfg.PATHS.TEST_PATH}/BackendControllerTest"):
            os.makedirs(f"{cfg.PATHS.TEST_PATH}/BackendControllerTest")
        cls.schema = "test."
        cls.controller = BackendController(
            database_uri=f"sqlite:///{TESTING_DB_PATH}")

        cls.example_llm_config_data = {
            "config": {"key": "val"}
        }
        cls.example_llm_config_patch = {
            "config": {"new_key": "new_val"}
        }
        cls.example_kb_config_data = {
            "config": {"key": "val"}
        }

    @classmethod
    def tearDownClass(cls):
        """
        Class method for setting tearing down test case.
        """
        del cls.controller
        del cls.schema
        del cls.example_llm_config_data
        del cls.example_kb_config_data
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
        gc.collect()


if __name__ == '__main__':
    unittest.main()
