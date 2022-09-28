import os

def str2float(des_type, val):
    if isinstance(val, float):
        return val
    if isinstance(val, int):
        return val

    removal_list = ["ohm", "Ohm", "ohms", "Ohms"]

    res_value_dict = {"k": "e3", "K": "e3",
                      "MEG": "e6", "M": "e6", "meg": "e6"
                      }

    val = val.replace(",", ".")
    if des_type == "resistor":
        for i in removal_list:
            val = val.replace(i, "")

        for i, j in res_value_dict.items():
            val = val.replace(i, j)

    return float(val)


class PowerRail:

    @property
    def fname_power(self):
        return self._prim_node_name + ".csv"

    @property
    def figure_save_name(self):
        return self._prim_node_name + ".png"

    @property
    def prim_source_refdes(self):
        return self._prim_refdes_pin.split(".")[0]

    @property
    def source_net_name(self):
        return self._prim_node_name.split("-")[-1]

    def __init__(self,
                 prim_refdes_pin,
                 voltage=1.2,
                 negative_pin=None,
                 sense_pin=None,
                 sec_refdes_pin_list=[],
                 sink_power_info=""
                 ):
        self._prim_refdes_pin = prim_refdes_pin
        self.sense_pin = sense_pin
        self.voltage = voltage
        self._prim_node_name = ""
        self.sec_refdes_pin_list = sec_refdes_pin_list
        self.sec_node_name_list = []
        self.sink_power_info = sink_power_info

        self.sinks = {}

    def export_sink_info(self):
        data = ["Node Name, Part Name, Value, pins\n"]
        for _, s in self.sinks.items():
            data.append(",".join([s.node_name, s.part_name, "", "-".join(s.pin_list)]) + "\n")

        fpath = os.path.join("temp", self.fname_power)
        with open(fpath, "w") as f:
            f.writelines(data)

    def import_sink_info(self):
        if self.sink_power_info:
            with open(self.sink_power_info) as f:
                info = f.readlines()
                info.pop(0)
                for i in info:
                    node_name, part_name, value = i.split(",")
                    value = value.replace("\n", "")
                    self.sinks[node_name].current = value


class Sink:

    def __init__(self, refdes, net_name, pin_list, node_name, current=0, part_name=""):
        self.refdes = refdes
        self.part_name = part_name
        self.net_name = net_name
        self.pin_list = pin_list
        self.current = current
        self.node_name = node_name
