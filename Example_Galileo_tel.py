from utils.power_tree_schematic import NetList
from utils.dcir_power_tree import DCIRPowerTree
from utils.dcir_config import DCIRConfig


DCIRPowerTree.GROUND = ["GND"]

targetfile = r"galileo_example\galileo.tel"
print(targetfile)
edb = NetList(targetfile)
edb.import_comp_definition(r"galileo_example\comp_definition.csv")
edb.remove_unmounted_components(r"galileo_example\remove_comp_list.csv")

app = DCIRPowerTree(edb, "2022.2")
app.add_power_rail("U3A1.14", voltage=3.3)
app.add_power_rail("U3A1.37", voltage=1.0)
app.add_power_rail("U2A4.B1", voltage=1.5, sink_power_info=r"galileo_example\U2A4-V1P5_S3.csv")
app.run(pdf_or_aedt="pdf")
#app.run(pdf_or_aedt="aedt")
app.close_aedt()