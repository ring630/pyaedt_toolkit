from utils.power_tree_schematic import NetList
from utils.dcir_power_tree import DCIRPowerTree
from utils.power_rail import PowerRail

DCIRPowerTree.GROUND = ["GND"]
DCIRPowerTree.COMP_PIN_EXCLUDE_LIST = ["U2A5.E1"]

targetfile = r"galileo_example\galileo.tel"
print(targetfile)
edb = NetList(targetfile)
edb.import_comp_definition(r"galileo_example\comp_definition.csv")
edb.remove_unmounted_components(r"galileo_example\remove_comp_list.csv")

app = DCIRPowerTree(edb, "2022.2")
app.add_power_rail("U3A1.14", voltage=3.3)
app.add_power_rail("U3A1.37", voltage=1.0)
app.run(nexxim_sch=True)
