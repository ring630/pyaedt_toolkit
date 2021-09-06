import os

os.chdir(os.path.dirname(os.path.abspath("")))
print(os.getcwd())

from utils.corepowertree import Configuration, CorePowerTree, Source, UserConfiguration



def test0_just_test():
    assert True

def test1_create_config_file():
    app_config = Configuration()
    assert app_config.create_default_config_file(path="_unittest_temp")

def test2_read_config_file():
    app_config = Configuration()
    app_config.edb_version = "2020.1"
    app_config.create_default_config_file(path="_unittest_temp")
    app_config.load_config_file(path="_unittest_temp")
    assert app_config.edb_version == "2020.1"
    #print(app_config.__dict__)

"""def test3_initial_edb():
    app_powertree = PowerTree()
    assert app_powertree.init_edb()"""

def test4_export_source_cfg():


    app_source_cfg = UserConfiguration(source=[Source(refdes="U3A1", voltage=1, output_net_name="BST_V1P0_S0"),
                                               Source(refdes="U3A1", voltage=3.3, output_inductor_refdes="L3A1")])

    assert app_source_cfg.create_example_cfg("_unittest_temp")

def test5_import_source_cfg():
    app_source_cfg = UserConfiguration()
    assert app_source_cfg.load_dcir_cfg("_unittest_temp")
    print(app_source_cfg.source_cfg)

def test5_get_vrm_output_net_name_from_RL():

    pass