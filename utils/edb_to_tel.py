import csv

from pyaedt import Edb
from get_galileo_example_board import get_galileo_exmaple_board

targetfile = get_galileo_exmaple_board()
edbapp = Edb(targetfile, edbversion="2022.2")

package = {}
nets = {}

for refdes, obj in edbapp.core_components.components.items():
    partname = obj.partname

    if not partname in package:
        if obj.type in ["Resistor", "Capacitor", "Inductor"]:
            if not obj.ind_value == "0":
                value = obj.ind_value
            elif not obj.cap_value == "0":
                value = obj.cap_value
            else:
                value = obj.res_value
            line = "! '{}' ! '{}' ; {} ".format(partname, value, refdes)
        else:
            line = "! '{}' ! ; {} ".format(partname, refdes)
        package[partname] = line
    else:
        line = package[partname]

        if len(line.split(",")[-1]) > 75:
            #line = line + ",\n"
            pass

        line = "{} {}".format(line, refdes)
        package[partname] = line

for refdes, comp_obj in edbapp.core_components.components.items():
    for pin, pin_obj in comp_obj.pins.items():
        net_name = pin_obj.net_name
        new_comp = "{}.{}".format(refdes, pin)

        if not net_name in nets:
            line = "'{}' ; ".format(net_name)
            nets[net_name] = line
        else:
            line = nets[net_name]
            if len(line.split(",")[-1]) > 75:
                pass
                #line = line + ",\n"
        line = "{} {}".format(line, new_comp)
        nets[net_name] = line



with open("../galileo_example/galileo.tel", "w") as f:
    f.writelines(["$PACKAGES\n"])
    f.writelines([i + "\n" for i in list(package.values())])
    f.writelines(["$NETS\n"])
    f.writelines([i + "\n" for i in list(nets.values())])
    f.writelines(["$A_PROPERTY\n"])

data = []
for refdes, comp_obj in edbapp.core_components.components.items():
    partname = comp_obj.partname

    if partname == "NONE":
        continue

    value = ""
    if comp_obj.type == "Resistor":
        value = comp_obj.res_value
    elif comp_obj.type == "Capacitor":
        value = comp_obj.cap_value
    elif comp_obj.type == "Inductor":
        value = comp_obj.ind_value

    data.append([partname, refdes, value])

with open("../galileo_example/bom_galileo.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Prod name", "RefDes", "Value"])
    writer.writerows(data)

edbapp.close_edb()