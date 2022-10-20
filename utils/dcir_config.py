import json


class IVComp:
    def __init__(self, refdes=None, power_pin=None, value=None, net_name=None, part_name=None,pin_list=None):
        self.refdes = refdes
        self.power_pin = power_pin
        self.value = value
        self.net_name = net_name
        self.part_name = part_name
        self.pin_list = pin_list

        self._node_name = None


    def to_dict(self):
        return {k: v for k, v in self.__dict__.items() if not k.startswith("_")}

    def import_dict(self, data):
        for k, v in data.items():
            k = k.lower()
            self.__dict__[k] = v
        return self


class SinglePowerConfig:
    def __init__(self):
        self.voltage = None
        self.main_v_comp = None
        self.main_v_comp_pin = None
        self.v_comp = {}
        self.i_comp = {}

    def to_dict(self):
        def find_recur(x, data):
            _data = data
            for k, val in x.__dict__.items():
                if isinstance(x, dict):
                    find_recur(val, _data[k])
                elif isinstance(val, IVComp):
                    _data[k] = val.to_dict()
                else:
                    _data[k] = val
            return _data
        data = {}
        return find_recur(self, data)

    def import_dict(self, fpath):
        def find_recur(data):
            for k, val in data.items():
                k = k.lower()
                if k not in ["v_comp", "i_comp"]:
                    self.__dict__[k] = val
                else:
                    for k1, val1 in val.items():
                        self.__dict__[k][k1] = IVComp().import_dict(val1)
        if isinstance(fpath, dict):
            data = fpath
        else:
            with open(fpath, "r") as f:
                data = json.loads(f.read())
        find_recur(data)
        self.voltage = list(self.v_comp.values())[0].value
        self.main_v_comp = list(self.v_comp.values())[0].refdes
        self.main_v_comp_pin = list(self.v_comp.values())[0].power_pin


class DCIRConfig:
    def __init__(self, cfg_file_path=""):
        self.edb_version = ""
        self.layout_file_name = ""
        self.gnd_net_name = ""
        self.removal_list = []
        self.comp_definition = {}
        self.power_configs = {}

        self.import_config(cfg_file_path)

    def import_config(self, file_path):
        def find_recur(data):
            for k, val in data.items():
                k = k.lower()
                if not k == "power_configs":
                    self.__dict__[k] = val
                else:
                    for k1, val1 in val.items():
                        sp = SinglePowerConfig()
                        sp.import_dict(val1)
                        self.__dict__[k][k1] = sp

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.loads(f.read())
        find_recur(data)

    def export_config(self, file_path):
        cfg = {key: value for key, value in self.__dict__.items()}
        temp = []
        for val in cfg["power_config"]:
            temp.append(val.export())
        cfg["power_config"] = temp

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=4)
