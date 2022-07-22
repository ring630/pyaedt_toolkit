from utils.main_edb import PowerTree
from utils.power_rail import PowerRail
from utils.galileo_example import get_galileo_exmaple_board


PowerTree.EDB_VERSION = "2022.1"
PowerTree.TP_PRIFIX = ["TP"]
PowerTree.REPLACE_BY_RES = ["F"]
PowerTree.CONNECTOR_PRIFIX = ["X"]
PowerTree.GROUND = ["GND"]
PowerTree.COMP_EXCLUDE_LIST = ["J2A1", "CR3A1", "DS2A1", "J1A6"]
PowerTree.COMP_PIN_EXCLUDE_LIST = ["U2A5.E1"]

targetfile = get_galileo_exmaple_board()
print(targetfile)
PowerTree(
    edb_path=targetfile,
    bom="",
    power_library_local="",
    power_rail_list=[PowerRail(prim_refdes_pin="U3A1.37", voltage=1.0,
                               sink_power_info="galileo_power_lib\\U3A1-BST_V1P0_S0.csv"),
                     PowerRail(prim_refdes_pin="U3A1.14", voltage=3.3),
                     ],
    #nexxim_sch=True
)
