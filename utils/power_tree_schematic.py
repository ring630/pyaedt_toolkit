import re

from .power_tree_base import PowerTreeBase
from .power_rail import str2float

class Component:

    @property
    def res_value(self):
        return self.value

    def __init__(self, refdes, cmp_type, partname, value=""):
        self.refdes = refdes
        self.type = cmp_type
        self.value = value
        self.partname = partname
        self.is_enabled = True


class TelNetList:

    @property
    def core_components(self):
        return self

    def __init__(self, tel_file):
        self._tel_file = tel_file
        self._rats = None
        self.components = {}

        self._get_rats_from_netlist()


        self._build_netlist()

    def _build_netlist(self):
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

    def database_preprocess(self):
        pass

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


class PowerTreeTel(PowerTreeBase):

    def __init__(self, fpath, edb_version="2022.2"):
        self.tel_path = fpath
        self.appedb = TelNetList(self.tel_path)
        PowerTreeBase.__init__(self, self.appedb, edb_version)

    def load_bom(self, bom_file):
        pass
