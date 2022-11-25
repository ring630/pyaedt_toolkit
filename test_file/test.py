import os
from dcir_power_tree import SinglePowerConfig, PowerTreeConfig
from dcir_power_tree import PowerTreeExtraction
from dcir_power_tree import DCIRAnalysis

test_folder = r"C:\Users\hzhou\AppData\Roaming\JetBrains\PyCharmCE2022.1\scratches\power_tree_galileo"


def test_0():
    assert os.path.isfile(fpath_single_power_config)
    assert os.path.isfile(fpath_dcir_init_config)

"""Power tree extraction"""

def test_single_power_config():
    app = SinglePowerConfig()
    app.import_dict(fpath_single_power_config)


def test_dcir_config():
    os.chdir(r"C:\Users\hzhou\OneDrive - ANSYS, Inc\PyCharm_project\DCIR_Automation_github\test_file")
    #app = PowerTreeConfig("Galileo.json")
    app = PowerTreeConfig("Galileo.xlsx")
    app.export_config_excel("test.xlsx")

    print("end")

def test_dcir_power_tree_pdf():
    #app = PowerTreeExtraction(test_folder, "Galileo.json")
    app = PowerTreeExtraction(test_folder, "vrm_cfg.xlsx")
    app.extract_power_tree(False)


def test_dcir_power_tree_aedt():
    #app = PowerTreeExtraction(test_folder, "Galileo.json")
    app = PowerTreeExtraction(test_folder, "vrm_cfg.xlsx")
    app.extract_power_tree(True)


"""DCIR configuration"""
def test_dcir_analysis():
    #Desktop()
    app = DCIRAnalysis(test_folder, r"extraction_result\configuration.json")
    app.config_edb(remove_gnd=False)
