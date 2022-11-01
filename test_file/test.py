import os
from ..utils.configuration import SinglePowerConfig, PowerTreeConfig
from ..utils.power_tree_extraction import PowerTreeExtraction
from ..utils.dcir_analysis import DCIRAnalysis

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
    app.export_config_excel(fpath_dcir_init_config.replace(".json", ".xlsx"))
    print("end")


def test_dcir_power_tree_pdf():
    app = PowerTreeExtraction(test_folder, "dcir_config.json")
    app.extract_power_tree(False)


def test_dcir_power_tree_aedt():
    app = PowerTreeExtraction(test_folder, "dcir_config.json")
    app.extract_power_tree(True)


"""DCIR configuration"""
def test_dcir_analysis():
    from pyaedt import Desktop
    #Desktop()
    app = DCIRAnalysis(test_folder, r"extraction_result\Galileo.json")
    app.config_edb(remove_gnd=False)
