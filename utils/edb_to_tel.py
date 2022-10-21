class EdbToNetlist:

    def __init__(self, edbapp):
        self.lines = []
        package = {}
        nets = {}

        for refdes, obj in edbapp.core_components.components.items():
            partname = obj.part_name

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

        self.lines.extend(["$PACKAGES\n"])
        self.lines.extend([i + "\n" for i in list(package.values())])
        self.lines.extend(["$NETS\n"])
        self.lines.extend([i + "\n" for i in list(nets.values())])
        self.lines.extend(["$A_PROPERTY\n"])
