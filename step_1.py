
from utils.dcir_power_tree import DCIRPowerTree



DCIRPowerTree(r"example\Input_config.json")

"""targetfile = r"example\galileo.tel"
print(targetfile)
edb = NetList(targetfile)
edb.import_comp_definition(r"example\comp_definition.csv")
edb.remove_unmounted_components(r"example\remove_comp_list.csv")

app = DCIRPowerTree(edb, "2022.2")
app.add_power_rail("U3A1.14", voltage=3.3)
app.add_power_rail("U3A1.37", voltage=1.0)
app.run(pdf_or_aedt="pdf")
#app.run(pdf_or_aedt="aedt")
app.close_aedt()"""