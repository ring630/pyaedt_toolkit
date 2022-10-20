import json
from collections import OrderedDict


class SinglePowerConfig:

    @property
    def node_name(self):
        return "{}-{}".format(self._refdes, self._power_pin)

    @property
    def net_name(self):
        v_comps = list(self.v_comp.values())
        if len(v_comps):
            return v_comps[0]["Net_name"]
        else:
            return ""

    @property
    def fname_power(self):
        return self.node_name + ".csv"

    @property
    def figure_save_name(self):
        return self.node_name + ".png"

    @property
    def refdes(self):
        if not len(self.v_comp):
            return list(self.v_comp.values())[0]["Refdes"]

    @property
    def power_pin(self):
        if not len(self.v_comp):
            return list(self.v_comp.values())[0]["Power_pin"]

    @property
    def voltage(self):
        if not len(self.v_comp):
            return list(self.v_comp.values())[0]["Voltage"]

    def __init__(self, refdes=None, power_pin=None, voltage=None):

        self.v_comp = {}
        self.i_comp = {}
        self.add_power(refdes, power_pin, voltage, None, None)

    def add_power(self, refdes, power_pin, value, net_name, pin_list):
        name = "{}-{}".format(refdes, net_name)
        self.v_comp[name] = {"Refdes": refdes,
                             "Power_pin": power_pin,
                             "Value": value,
                             "Net_name": net_name,
                             "Pin_list": pin_list}

    def add_current(self, refdes, power_pin, value, net_name, pin_list):
        name = "{}-{}".format(refdes, net_name)
        self.i_comp[name] = {"Refdes": refdes,
                             "Power_pin": power_pin,
                             "Value": value,
                             "Net_name": net_name,
                             "Pin_list": pin_list}

    def export(self):
        data = {
            "NAME": self.node_name,
            "NET_NAME": self.net_name,
            "Voltage": self.voltage,
            "V_COMP": {},
            "I_COMP": {}
        }
        def iter_power(i, data_dict):
            for idx, val in i.items():
                if not isinstance(val, dict):
                    data_dict[idx] = val
                else:
                    data_dict[idx] = {}
                    iter_power(val, data_dict[idx])
            return data_dict

        iter_power(self.i_comp, data["V_COMP"])
        iter_power(self.i_comp, data["I_COMP"])
        return data


class DCIRConfig:
    def __init__(self, cfg_file_path=""):
        self.edb_version = ""
        self.layout_file_name = ""
        self.gnd_net_name = ""
        self.removal_list = []
        self.comp_definition = {}
        self.power_config = []

        self.import_config(cfg_file_path)

    def add_single_power(self, refdes, power_pin, voltage):
        self.power_config.append(SinglePowerConfig(refdes, power_pin, voltage))

    def import_config(self, file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.loads(f.read())
        for key, value in data.items():
            if not key == "power_config":
                self.__dict__[key] = value
            else:
                sp = SinglePowerConfig()
                for iv_comp in value:
                    for k, v in iv_comp.items():
                        sp.__dict__[k] = v
                self.power_config.append(sp)

    def export_config(self, file_path):
        cfg = {key: value for key, value in self.__dict__.items()}
        temp = []
        for val in cfg["power_config"]:
            temp.append(val.export())
        cfg["power_config"] = temp

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    cfg = DCIRConfig()
    cfg.add_single_power(1, 2, 3)
    c = cfg.export_config("Input_config.json")

