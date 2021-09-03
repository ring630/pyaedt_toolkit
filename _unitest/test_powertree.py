from unittest import TestCase

import os

os.chdir(os.path.dirname(os.path.abspath("")))
print(os.getcwd())

from utils.corepowertree import Configuration, CorePowerTree, Source, UserSourceConfig, SinkSourceCfg, Library

class TestClass(TestCase):

    def setup_class(self):
        self.app_powertree = CorePowerTree()
        self.app_powertree.init_edb()

    def teardown_class(self):
        self.app_powertree.close_edb()

    def test1_create_config_file(self):
        app_config = Configuration()
        assert app_config.create_default_config_file(path="_unittest_temp")

    def test2_load_config_file(self):
        app_config = Configuration()
        app_config.edb_version = "2020.1"
        app_config.create_default_config_file(path="_unittest_temp")
        app_config.load_config_file(path="_unittest_temp")
        assert app_config.edb_version == "2020.1"
        # print(app_config.__dict__)

        """    def test3_initial_edb(self):
        return True
        app_config = Configuration()
        app_config.layout_file_name="Galileo.brd"
        app_powertree = PowerTree(app_config)
        assert app_powertree.init_edb()"""

    def test4_create_example_source_cfg(self):
        app_source_cfg = UserSourceConfig(referenece_net_name="GND",
                                          node_to_ground="U3A1",
                                          source=[Source(refdes="U3A1", voltage=1, output_net_name="BST_V1P0_S0"),
                                              Source(refdes="U3A1", voltage=3.3,
                                                          output_inductor_refdes="L3A1")])

        assert app_source_cfg.create_example_cfg("_unittest_temp")

    def test5_load_source_cfg(self):
        app_source_cfg = UserSourceConfig()
        assert app_source_cfg.load_cfg("_unittest_temp")
        print(app_source_cfg.source_cfg)

    def test5_get_vrm_output_net_name_from_RL(self):
        self.app_powertree = CorePowerTree()
        self.app_powertree.init_edb()
        #assert self.app_powertree._find_vrm_output_net_name_from_inductor_refdes(vrm_refdes="U3A1", inductor_refdes="L3A1")

    def test6_extract_power_tree(self):
        self.app_powertree = CorePowerTree()
        self.app_powertree.init_edb()
        cfg = SinkSourceCfg(refdes="U3A1", voltage=3.3, output_inductor_refdes="L3A1")

        sink_source_cfg = self.app_powertree.extract_power_tree(cfg)

        assert sink_source_cfg

    def test7_library(self):
        app_lib = Library()
        app_lib.create_example_library("_unittest_temp")

        app_lib = Library()
        app_lib.import_library("_unittest_temp")
