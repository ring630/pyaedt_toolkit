from utils.main_edb import PowerTree, PowerRail



PowerTree.EDB_VERSION = "2022.1"
PowerTree.TP_PRIFIX = ["TP"]
PowerTree.FUSE_PRIFIX = ["F"]
PowerTree.CONNECTOR_PRIFIX = ["X"]
PowerTree.GROUND = ["GND"]

PowerTree(
    edb_path="Galileo.aedb",
    bom="",
    power_library_local="",
    power_rail_list=[PowerRail(prim_refdes_pin="U3A1.37", voltage=1.0,
                               sink_power_info="galileo.aedb\\U3A1-BST_V1P0_S0.csv"),
                     PowerRail(prim_refdes_pin="U3A1.14", voltage=3.3),
                     ],
)
