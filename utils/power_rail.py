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
        return self._node_name + ".csv"

    @property
    def figure_save_name(self):
        return self._node_name + ".png"

    @property
    def source_refdes(self):
        return self._refdes_pin.split(".")[0]

    @property
    def source_net_name(self):
        return self._node_name.split("-")[-1]

    def __init__(self,
                 refdes_pin,
                 voltage=1.2,
                 sense_pin=None,
                 sink_power_info="",
                 node_to_ground=True,
                 ):
        self._refdes_pin = refdes_pin
        self.sense_pin = sense_pin
        self.voltage = voltage
        self._node_name = ""

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
                    print(i.split(","))
                    node_name, part_name, value = i.split(",")[:3]
                    value = value.replace("\n", "")
                    self.sinks[node_name].current = value


class PowerRailMultiVrm(PowerRail):
    def __init__(self):
        self.sec_refdes_pin_list = None

class Sink:

    def __init__(self, refdes, net_name, pin_list, node_name, current=0, part_name=""):
        self.refdes = refdes
        self.part_name = part_name
        self.net_name = net_name
        self.pin_list = pin_list
        self.current = current
        self.node_name = node_name
