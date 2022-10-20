import os
from ..utils.dcir_config import SinglePowerConfig, DCIRConfig
from ..utils.dcir_power_tree import DCIRPowerTree

test_folder = os.path.dirname(__file__)
fpath_single_power_config = os.path.join(test_folder, "single_power_config.json")
fpath_dcir_config = os.path.join(test_folder, "dcir_config.json")


def test_0():
    assert os.path.isfile(fpath_single_power_config)
    assert os.path.isfile(fpath_dcir_config)


def test_single_power_config():
    app = SinglePowerConfig()
    app.import_dict(fpath_single_power_config)


def test_dcir_config():
    app = DCIRConfig(fpath_dcir_config)
    print("end")


def test_dcir_power_tree():
    app = DCIRPowerTree(fpath_dcir_config)
    app.run()
    print("end")