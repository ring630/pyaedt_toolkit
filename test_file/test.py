import os
from ..utils.configuration import SinglePowerConfig, PowerTreeConfig
from ..utils.power_tree_extraction import PowerTreeExtraction
from ..utils.dcir_analysis import DCIRAnalysis

#test_folder = os.path.dirname(__file__)
test_folder = r"C:\Users\hzhou\OneDrive - ANSYS, Inc\PyCharm_project\DCIR_Automation_github\test_file"
fpath_single_power_config = os.path.join(test_folder, "single_power_config.json")
fpath_dcir_init_config = os.path.join(test_folder, "dcir_config.json")
fpath_dcir_full_config = os.path.join(test_folder, "extraction_result", "Galileo.json")


def test_0():
    assert os.path.isfile(fpath_single_power_config)
    assert os.path.isfile(fpath_dcir_init_config)

"""Power tree extraction"""

def test_single_power_config():
    app = SinglePowerConfig()
    app.import_dict(fpath_single_power_config)


def test_dcir_config():
    app = PowerTreeConfig(fpath_dcir_init_config)
    print("end")


def test_dcir_power_tree_pdf():
    app = PowerTreeExtraction(fpath_dcir_init_config)
    app.extract_power_tree()

def test_dcir_power_tree_aedt():
    app = PowerTreeExtraction(test_folder, "dcir_config.json")
    app.extract_power_tree("aedt")

"""DCIR configuration"""

def test_dcir_analysis():
    app = DCIRAnalysis(fpath_dcir_full_config)
    app.config_edb()
