# Introduction 
DCIR_Automation is intended to improve DCIR simulation workflow for complex PCB. This project is built on top of [PyAEDT](https://github.com/pyansys/PyAEDT). DCIR_Automation is licenced under the [MIT License](https://github.com/pyansys/PyAEDT/blob/main/LICENSE).

DCIR_Automation interacts directly with Electronics Database(EDB) which can be loaded into both SIwave and Ansys Electronics Desktop(AEDT).  Design data, in several industry-standard formats, can be converted into EDB format. Read AEDT Help for more information. [HFSS 3D Layout Help > Layout and Circuit Import Export Operations > Importing Layout Design Data](https://ansyshelp.ansys.com/account/secured?returnurl=/Views/Secured/Electronics/v212/en/home.htm%23../Subsystems/HFSS3DLayout/Content/3DLayout/ImportingLayoutDesignData.htm%3FTocPath%3DHFSS%25203D%2520Layout%7CHFSS%25203D%2520Layout%2520Help%7CLayout%2520and%2520Circuit%2520Import%2520Export%2520Operations%7CImporting%2520Layout%2520Design%2520Data%7C_____0)

The Ansys Electronics Desktop supports Extracta Import from Cadence. Note that Extracta.Exe is
a Cadence supplied executable and must be installed on your machine and on your executable
path for this to work.

DCIR_Automation extends existing DCIR workflow functionalities as below.

1, Extract power trees from EDB by user provided voltage regulator module(VRM) reference designator(Refdes) together with VRM output net name or output inductor Refdes.

2, List all sink components on power tree per VRM.

3, Assign current to sink components from user defined local library.  

# Getting Started
1. download and install Anaconda3. https://www.anaconda.com/products/individual
2. open anaconda prompt to create a virtual environment dcir_automatio and install PyAEDT
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#create a virtual environment
conda create —-name dcir_automation python= 3.8 pandas numpy matplotlib ipython

#list all environments
conda info --envs             

#activate the new environement
conda activate dcir_automation      

#install pyvista and PyAEDT
pip install pyvista                                       
pip install pyaedt
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
3. Download dcir_automation code and unzip it to jupyter notebook working directory.
4. Start Jupyter Notebook
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
jupyter notebook
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Run on Example Project
## Prepare configuration file in .json format
Execute below code to create an example configuration file.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    from utils.dcir_workflow import UserConfiguration

    uc = UserConfiguration() 

    uc.create_default_config_file()
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Configuration.json will be created in working directory
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
{
    "project_config": {
        "edb_version": "2021.2",
        "layout_file_name": "Galileo.aedb", 
        "reference_net_name": "GND",
        "node_to_ground": "U3A1"
    },
    "sources": [
        {
            "refdes": "U3A1",
            "voltage": 1,
            "output_net_name": "BST_V1P0_S0",
            "output_inductor_refdes": "",
            "power_net_name": ""
        },
        {
            "refdes": "U3A1",
            "voltage": 3.3,
            "output_net_name": "",
            "output_inductor_refdes": "L3A1",
            "power_net_name": ""
        }
    ]
}
# Galileo.aedb is located in <working directory>:\layout_database 
# There are two power trees to be extracted by different approaches.
# 1, VRM Refdes + output_net_name
# 2, VRM Refdes + output_inductor_refdes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

## Prepare component library
Execute below code to create an example library file.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
from utils.dcir_workflow import Library

Library().create_example_library()
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

## Library.json will be created in working directory
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
{
    "IPD031-201": {
        "part_name": "IPD031-201",
        "power_rails": {
            "Core_1V0": {
                "pins": "Y14-AB14-AD14-V14-Y20-Y18-Y16-AB20-AB18-T18-V20-V18-V16",
                "current": 10
            }
        }
    },
    "E17764-001": {
        "part_name": "E17764-001",
        "power_rails": {
            "P1V0": {
                "pins": "10",
                "current": 1
            }
        }
    }
}
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
## Load layout file and extract power tress
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
from utils.dcir_workflow import DcirWorkflow

app_dcir = DcirWorkflow()
app_dcir.extract_power_tree()
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

## Check if power trees are correctly extracted.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
EDB Version 2021.1
EDB Standalone True
Database Opened
Cell Galileo Opened
C:\Anaconda3\envs\AnsysEnv\lib\site-packages\pyaedt\dlls\EDBLib\DataModel.dll
Refreshing the Components dictionary.
Objects Initialized
Builder Initialized
Edb Initialized
531 components
432 nets
initialization finished.. Elapsed time = 3.6 seconds
Found VRM U3A1 output net_name BST_V3P3_S5 
Extracting U3A1-BST_V1P0_S0-
FB3L1  is not connected to ref net
Extracting U3A1-BST_V3P3_S5-L3A1
Found VRM U3A1 output net_name BST_V3P3_S5 
J1A6  is not connected to ref net
CR3A1  is not connected to ref net
DS2A1  is not connected to ref net
****************************************
*** Extraction is done. Please to to next step ***
****************************************

# J1A6, CR3A1, DS2A1 have no connect to reference net and are not sink components. 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

## Load current from library
Execute below code
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
app_dcir.refresh_library()
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

### Check file library_to_be_filled.json
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
{
    "G94441-001": {
        "part_name": "G94441-001",
        "power_rails": {
            "U2M1-V3P3_S5": {
                "pins": "A2-B2-C2",
                "current": 0
            }
        }
    },
    "G79625-001": {
        "part_name": "G79625-001",
        "power_rails": {
            "J2A1-V3P3_S5": {
                "pins": "4",
                "current": 0
            }
        }
    },
    "G84017-001": {
        "part_name": "G84017-001",
        "power_rails": {
            "J4A1-V3P3_S5": {
                "pins": "1",
                "current": 0
            }
        }
    }
}
# Three power input has no current definition in library file.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

### fill in current from component specification and execute below code again until library_to_be_filled.json is empty
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
app_dcir.refresh_library()
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

## Solve DCIR
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
app_dcir.analyze()
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

## Check result
open file working directory:/result/date time/U3A1-BST_V1P0_S0-.json
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    {
    "powertree_id": "U3A1-BST_V1P0_S0-",
    "vrm_refdes": "U3A1",
    "voltage": 1,
    "sinks": [
        {
            "refdes": "U2A5",
            "current": 10,
            "net_name": "V1P0_S0",
            "part_name": "IPD031-201",
            "pins": "Y14-AB14-AD14-V14-Y20-Y18-Y16-AB20-AB18-T18-V20-V18-V16",
            "comp_type": "IC",
            "pos_voltage": 0.4423362433085,
            "neg_voltage": 0.005761736934866,
            "voltage": 0.43657450637363404
        }
    ]
}
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

open aedt project for post processing working directory:\result\Galileo.aedt
    
