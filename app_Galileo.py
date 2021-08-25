
from utils.powertree import PowerTree

"""
******** User Action *******

Preparation
1, create a project folder under DCIR_Automation and name it. example_project is used as the folder name for example.
2, create folder EDB under project folder
3, copy .aedb folder under EDB folder. edb.def should be in .aedb folder.
4, copy comp_lib_template.csv into project folder and rename it as comp_lib.csv
"""

# specifiy project folder, edb folder and edbversion
app = PowerTree(project_dir=r"example_project",
                aedb_dir_name="Galileo.aedb",
                edbversion="2021.1"
                )

# specify global reference net name
app.define_reference_net("GND")

# exclude components from power tree extraction
app.define_excluded_componenets(["J1A61"])

# Load edb
app.Initialize_EDB()

# User defined voltage regulator refdes, voltage and output net name
app.extract_power_tree(vrms={"BST_V1P0_S0": {"VOLTAGE": 1, "VRM_REFDES": "U3A1"},
                            "BST_V3P3_S5": {"VOLTAGE": 3.3, "VRM_REFDES": "U3A1"},
                             })

# specify component power consumption library file. library file should be put in project folder
app.assign_component_current("comp_lib.csv")


app.power_tree_cleaning()


"""
0: "Only check components on power tree"
1: "Only export DCIR project"
2: "Simulate in Non-graphic mode"
"""
mode = 2

if mode == 0:
    # extracted power trees are stored under project_folder/result/[datetime]/.
    # For instance, /result/210820-08-47-41/U3A1-BST_V1P0_S0.csv
    app.export_powertree_to_csv()
    # components without current assignment are listed in log/comp_wo_current.csv
    app.export_component_wo_current()

    """
    ******** User Action *******
    
    1, check project_folder/log/comp_wo_current.csv file. Components without current assignment are listed here.
    2, open comp_lib.csv file, copy/paste components here from step 1. fill in current comsumption from datasheet. 
    3, repeat mode 0 until no component show up in comp_wo_current.csv
    4, check if all components have current assignment in power tree csv files. 
    """

elif mode == 1:
    # configure EDB for DCIR analysis
    app.config_dcir()
    # create aedt project from EDB without solving
    app.create_aedt_project(solve=False)

    """
    ******** User Action *******
    
    1, open aedt project at project_folder/result/configured_edb.aedt.
    2, check sinks and sources.
    3, analysis DCIR in aedt
    """

elif mode == 2:
    # configure EDB for DCIR analysis
    app.config_dcir()
    # create aedt project from EDB and solve in non-graphic mode
    app.create_aedt_project(solve=True)
    # read results and fill voltage information into esult/[datetime]/
    app.load_result()

    """
    ******** User Action *******

    1, check results under project_folder/result/[datetime]/
    2, open aedt project for post-processing at project_folder/result/configured_edb.aedt.
    """