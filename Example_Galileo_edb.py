from utils.power_tree_edb import PowerTreeEdb
from utils.power_rail import PowerRail
from utils.get_galileo_example_board import get_galileo_exmaple_board


PowerTreeEdb.EDB_VERSION = "2022.1"
PowerTreeEdb.TP_PRIFIX = ["TP"]
PowerTreeEdb.REPLACE_BY_RES = ["F"]
PowerTreeEdb.CONNECTOR_PRIFIX = ["X"]
PowerTreeEdb.GROUND = ["GND"]
PowerTreeEdb.COMP_EXCLUDE_LIST = ["J2A1", "CR3A1", "DS2A1", "J1A6"]
PowerTreeEdb.COMP_PIN_EXCLUDE_LIST = ["U2A5.E1"]

targetfile = get_galileo_exmaple_board()
print(targetfile)
PowerTreeEdb(
    fpath=targetfile,
    bom="",
    power_rail_list=[PowerRail(prim_refdes_pin="U3A1.37", voltage=1.0,
                               sink_power_info="galileo_example\\U3A1-BST_V1P0_S0.csv"),
                     PowerRail(prim_refdes_pin="U3A1.14", voltage=3.3),
                     ],
    #nexxim_sch=True
)
