
from utils.powertree import Configuration


def test0_just_test():
    assert True

def test1_create_config_file():
    app_config = Configuration()
    assert app_config.create_default_config_file(path="temp")

def test2_read_config_file():
    app_config = Configuration()
    app_config.edb_version = "2020.1"
    app_config.create_default_config_file(path="temp")
    app_config.read_config_file(path="temp")
    assert app_config.edb_version == "2020.1"
    #print(app_config.__dict__)

"""test = Test()
#test.test1_create_config_file()
test.test2_read_config_file()"""