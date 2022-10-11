from utils.power_tree_edb import PowerTreeEdb
from utils.get_galileo_example_board import get_galileo_exmaple_board

PowerTreeEdb.DEFAULT_SINK_CURRENT = 1

PowerTreeEdb.TP_PRIFIX = ["TP"]
PowerTreeEdb.REPLACE_BY_RES = ["F"]
PowerTreeEdb.CONNECTOR_PRIFIX = ["X"]
PowerTreeEdb.GROUND = ["GND"]
PowerTreeEdb.COMP_EXCLUDE_LIST = ["J2A1", "CR3A1", "DS2A1", "J1A6"]
PowerTreeEdb.COMP_PIN_EXCLUDE_LIST = ["U2A5.E1"]

targetfile = get_galileo_exmaple_board()
print(targetfile)
app = PowerTreeEdb(fpath=targetfile, edb_version="2022.2")

app.add_power_rail("U3A1.14", voltage=3.3)
app.add_power_rail("U3A1.37", voltage=1.0,
                   sink_power_info="galileo_example\\U3A1-BST_V1P0_S0.csv")

app.run(nexxim_sch=True)
app.setup_dcir()
app.analyze()
