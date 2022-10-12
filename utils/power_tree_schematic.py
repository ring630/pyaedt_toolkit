import re
import pandas as pd

from .dcir_power_tree import DCIRPowerTree
from .power_rail import str2float

class Component:

    @property
    def res_value(self):
        return self.value

    def __init__(self, refdes, cmp_type, part_name, value=""):
        self.refdes = refdes
        self.type = cmp_type
        self.value = value
        self.partname = part_name
        self.is_enabled = True


class NetList:

    @property
    def core_components(self):
        return self

    @property
    def _rats_by_index(self):
        return {i["refdes"][0]: i for i in self._rats}

    def __init__(self, file_path):
        self._tel_file = file_path
        self._rats = None
        self.components = {}

        self._get_rats_from_netlist()
        self._get_components_from_netlist()

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
                    """elif refdes.startswith("F"):
                    self.component[refdes] = Component(refdes, "resistor", pn, "0.001")"""
                elif refdes.startswith("L"):
                    self.components[refdes] = Component(refdes, "inductor", pn)
                elif refdes.startswith("C"):
                    self.components[refdes] = Component(refdes, "capacitor", pn)
                    """elif refdes.startswith("INC"):
                    self.component[refdes] = Component(refdes, "test_point", pn)
                elif refdes.startswith("X"):
                    self.component[refdes] = Component(refdes, "connector", pn)"""
                else:
                    self.components[refdes] = Component(refdes, "other", pn)

    def import_bom(self):
        pass

    def import_comp_definition(self, file_path):
        remove_list = []
        df = pd.read_csv(file_path, index_col=0)
        for part_name, val in df.iterrows():
            for refdes, obj in self.components.items():
                if obj.partname == part_name:
                    if val.Type == "Testpoint":
                        remove_list.append(refdes)
                    else:
                        print("update {}, {} -> {}, {} -> {}".format(refdes, obj.type, val.Type, obj.value, val.Value))
                        obj.type = val.Type
                        obj.value = val.Value
        for refdes in remove_list:
            self.components.pop(refdes)
            self._rats.remove(self._rats_by_index[refdes])
            print("Test point ", refdes, " is removed")

    def remove_unmounted_components(self, file_path):
        remove_list = []
        df = pd.read_csv(file_path, index_col=0)
        for refdes_remove, val in df.iterrows():
            print(refdes_remove, "is removed")
            self.components.pop(refdes_remove)
            for idx, i in enumerate(self._rats):
                if i["refdes"][0] == refdes_remove:
                    remove_list.append(i)
        for i in remove_list:
            self._rats.remove(i)

    def get_rats(self):
        return self._rats

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


class PowerTreeTel(DCIRPowerTree):

    def __init__(self, fpath, edb_version="2022.2"):
        self.tel_path = fpath
        self.appedb = NetList(self.tel_path)
        DCIRPowerTree.__init__(self, self.appedb, edb_version)

    def load_bom(self, bom_file):
        pass
