from utils.power_tree_schematic import PowerTreeSchematic
from utils.power_rail import PowerRail


PowerTreeSchematic.EDB_VERSION = "2022.1"
PowerTreeSchematic.TP_PRIFIX = ["TP", "INC"]
PowerTreeSchematic.REPLACE_BY_RES = ["F"]
PowerTreeSchematic.CONNECTOR_PRIFIX = ["X"]
PowerTreeSchematic.GROUND = ["GND"]
PowerTreeSchematic.COMP_EXCLUDE_LIST = ["J2A1", "CR3A1", "DS2A1", "J1A6"]
PowerTreeSchematic.COMP_PIN_EXCLUDE_LIST = ["D10000.V15", "D19000.9"]

PowerTreeSchematic.EXCLUE_CONNECTOR = True

targetfile = r"tel_example\core.tel"
print(targetfile)
PowerTreeSchematic(
    fpath=targetfile,
    bom="",
    power_rail_list=[PowerRail(prim_refdes_pin="D15501.6",
                               voltage=1.0,
                               sec_refdes_pin_list=["D15500.6"]
                               #sink_power_info="galileo_power_lib\\U3A1-BST_V1P0_S0.csv"
                               ),
                     ],
    nexxim_sch=True
)
