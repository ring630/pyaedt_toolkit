import json
from collections import OrderedDict


class SinglePowerConfig:

    @property
    def node_name(self):
        return self._refdes + "-" + self._power_pin

    @property
    def fname_power(self):
        return self.node_name + ".csv"

    @property
    def figure_save_name(self):
        return self.node_name + ".png"

    def __init__(self, refdes, power_pin, voltage):
        self._refdes, = refdes
        self._power_pin = power_pin

        self.voltage = voltage
        self.v_comp = {}
        self.i_comp = {}

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
        data = {}

        def iter_power(i, data_dict):
            for idx, val in i.items():
                if not isinstance(val, dict):
                    data_dict[idx] = val
                else:
                    data_dict[idx] = {}
                    iter_power(val, data_dict[idx])
            return data_dict

        print(iter_power(self.i_comp, data))


class DCIRConfig:
    def __init__(self, cfg_file_path=""):
        self.gnd_net_name = "GND"
        self.REMOVAL_LIST = []
        self.COMP_DEFINITION = {}
        self.power_config = SinglePowerConfig()

    def import_config(self):
        pass

    def export_config(self):
        cfg = {key: value for key, value in self.__dict__.items()}


if __name__ == '__main__':
    cfg = DCIRConfig()