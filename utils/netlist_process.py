import json
import re
from . import str2float


class CompDefinition:
    def __init__(self, cmp_type, part_name, value=""):
        self.type = cmp_type
        self.value = value
        self.part_name = part_name


class Component(CompDefinition):

    @property
    def res_value(self):
        return self.value

    def __init__(self, refdes, cmp_type, part_name, value=""):
        CompDefinition.__init__(self, cmp_type, part_name, value)
        self.refdes = refdes
        self.is_enabled = True


class NetList:

    def __init__(self, file_path):
        self._tel_file = file_path
        self._rats = None
        self.components = {}
        self.comp_definitions = {}

        self._get_rats_from_netlist()
        self._get_components_from_netlist()

    @property
    def core_components(self):
        return self

    @property
    def _rats_by_index(self):
        return {i["refdes"][0]: i for i in self._rats}

    def get_rats(self):
        return self._rats

    def _get_components_from_netlist(self):
        txt_lines = open(self._tel_file).read().replace(",\n", " ")

        start = re.search(r"\$PACKAGES", txt_lines).end()
        tmp = txt_lines[start:]
        end = re.search(r"[^']\$", tmp).start()
        packages = tmp[:end]
        for l in packages.split("\n"):
            if l == "":
                continue
            a, b = l.split(";")
            val_str = a.replace(" ", "").replace("'", "").split("!")[1:]
            if len(val_str) == 2:
                pn, val_str = val_str
            for refdes in b.split(" "):
                if refdes == "":
                    continue
                elif refdes.startswith("R"):
                    val_float = str2float("resistor", val_str)
                    self.components[refdes] = Component(refdes, "resistor", pn, val_float)
                elif refdes.startswith("L"):
                    self.components[refdes] = Component(refdes, "inductor", pn)
                elif refdes.startswith("C"):
                    self.components[refdes] = Component(refdes, "capacitor", pn)
                else:
                    self.components[refdes] = Component(refdes, "other", pn)

    def import_bom(self):
        pass

    def import_comp_definition(self, file_path):
        remove_list = []
        with open(file_path, "r") as f:
            data = json.loads(f.read())
        data = data["Definitions"]
        for part_name, val in data.items():
            for refdes, obj in self.components.items():
                if obj.part_name == part_name:
                    if val["Component_type"].capitalize() == "Testpoint":
                        remove_list.append(refdes)
                    elif val["Model_type"] == "RLC":
                        print(val)
                        comp_tpye = val["Component_type"]
                        comp_tpye = comp_tpye.capitalize() if len(comp_tpye) > 2 else comp_tpye.upper()
                        obj.type = comp_tpye
                        if obj.type == "Resistor":
                            obj.value = val["Res"]
                        elif obj.type == "Inductor":
                            obj.value = val["Ind"]
                        elif obj.type == "Capacitor":
                            obj.value = val["Cap"]
                        else:
                            pass
                    else:
                        pass
        for refdes in remove_list:
            self.components.pop(refdes)
            self._rats.remove(self._rats_by_index[refdes])
            print("Test point ", refdes, " is removed")

    def remove_capacitors(self):
        removal_list = []
        for refdes, comp in self.components.items():
            if comp.type.capitalize() == "Capacitor":
                removal_list.append(refdes)
        self.remove_comp_by_refdes(removal_list)

    def remove_resistor_by_value(self, value):
        removal_list = []
        for refdes, comp in self.components.items():
            if comp.type.capitalize() == "Resistor":
                if str2float("resistor", comp.value) > value:
                    removal_list.append(refdes)
        self.remove_comp_by_refdes(removal_list)

    def remove_comp_by_refdes(self, refdes_list):
        removal_list = []
        for refdes_remove in refdes_list:
            self.components.pop(refdes_remove)
            for idx, i in enumerate(self._rats):
                if i["refdes"][0] == refdes_remove:
                    removal_list.append(i)
        for i in removal_list:
            self._rats.remove(i)

    def remove_nets(self, net):
        if not isinstance(net, list):
            net = [net]
        rat_remove_list = []
        for n in net:
            for rat in self._rats:
                temp_list = []
                for idx, n1 in enumerate(rat["net_name"]):
                    if n1 == n:
                        temp_list.append(idx)
                rat["refdes"] = [i for idx, i in enumerate(rat["refdes"]) if idx not in temp_list]
                rat["pin_name"] = [i for idx, i in enumerate(rat["pin_name"]) if idx not in temp_list]
                rat["net_name"] = [i for idx, i in enumerate(rat["net_name"]) if idx not in temp_list]
                if not len(rat["refdes"]):
                    rat_remove_list.append(rat)
        for rat in rat_remove_list:
            self._rats.remove(rat)
        return

    def _get_rats_from_netlist(self):
        ############################
        # Find $NET block in tel file
        txt_lines = open(self._tel_file).read().replace(",\n", " ")
        start = re.search(r"\$NETS", txt_lines).end()
        sink_comp = txt_lines[start:]
        end = re.search(r"[^']\$", sink_comp).start()
        nets = sink_comp[:end]

        ############################
        # Find rats
        ratlist_pin = {}

        for l in nets.split("\n"):
            if l == "":
                continue
            net_name, refdes_pin = l.split(";")
            net_name = net_name.replace(" ", "").replace("'", "")
            net_name = net_name.replace("$", "").replace("-", "_")
            refdes_pin = refdes_pin.lstrip(" ").rstrip(" ")

            comp_list = [i for i in refdes_pin.split(" ")]
            ratlist_pin[net_name] = comp_list

        edb_rats = {}
        for net_name, comp in ratlist_pin.items():
            for i in comp:
                refdes, pin = i.split(".")
                if not refdes in edb_rats:
                    edb_rats[refdes] = {"refdes": [refdes],
                                        "pin_name": [pin],
                                        "net_name": [net_name]}
                else:
                    edb_rats[refdes]["refdes"].append(refdes)
                    edb_rats[refdes]["pin_name"].append(pin)
                    edb_rats[refdes]["net_name"].append(net_name)

        self._rats = list(edb_rats.values())

    def _get_component_definitions(self):
        for refdes, props in self.components.items():
            part_name = props.part_name
            if part_name not in self.comp_definitions:
                self.comp_definitions[part_name] = CompDefinition(props.type, props.part_name, props.value)
