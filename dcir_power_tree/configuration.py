import json

import pandas as pd


class IVComp:
    def __init__(self, refdes=None, power_pin=None, value=None, net_name=None, part_name=None, pin_list=None):
        self.refdes = refdes
        self.power_pin = power_pin
        self.value = value
        self.net_name = net_name
        self.part_name = part_name

        self.power_name = ""
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

        self._node_name = None

    def to_dict(self):
        def find_recur(x, data):
            _data = data
            for k, val in x.items():
                if isinstance(val, dict):
                    _data[k] = {}
                    find_recur(val, _data[k])
                elif isinstance(val, IVComp):
                    _data[k] = val.to_dict()
                else:
                    _data[k] = val
            return _data

        data = {}
        data = find_recur(self.__dict__, data)
        for k, val in data["i_comp"].items():
            val.pop("power_pin")
        return data

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
        self._node_name = list(self.v_comp.values())[0]._node_name


class PowerTreeConfig:
    def __init__(self, cfg_file_path=""):
        self.edb_version = ""
        self.layout_file_name = ""
        self.power_lib_file = ""
        self.gnd_net_name = ""
        self.resistor_removal_threshold = 0
        self.removal_list = []
        self.comp_definition = {}
        self.power_configs = {}
        self.custom_comps = {}
        self.all_power_nets = []
        if cfg_file_path.endswith(".json"):
            self.import_config_json(cfg_file_path)
        else:
            self.import_config_excel(cfg_file_path)

    def import_config_json(self, file_path):
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

    def _get_cfg_dict(self):
        cfg = {key: value for key, value in self.__dict__.items()}
        power_cfg = {}
        i = 0
        for k, val in cfg["power_configs"].items():
            if val._node_name:
                power_cfg[val._node_name] = val.to_dict()
            else:
                power_cfg[str(i)] = val.to_dict()
                i = i + 1
        cfg["power_configs"] = power_cfg
        return cfg

    def export_config_json(self, file_path):
        cfg = self._get_cfg_dict()

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=4)

        # with pd.ExcelWriter(file_path.replace(".json", ".xlsx")) as writer:
        #    for pwr, content in power_cfg.items():
        #        pd.DataFrame(content["i_comp"]).transpose().to_excel(writer, sheet_name=pwr)
        power_cfg = cfg["power_configs"]
        data = {}
        for pwr, content in power_cfg.items():
            i_comps = content["i_comp"]
            for _, props in i_comps.items():
                part_name = props["part_name"]
                pin_list = props["pin_list"]
                value = props["value"]

                power_name = props["power_name"] if "power_name" in props else pin_list
                if part_name not in data:
                    data[part_name] = {power_name: {"pin_list": pin_list,
                                                    "value": value}}
                elif power_name not in data[part_name]:

                    data[part_name][power_name] = {"pin_list": pin_list,
                                                   "value": value}

        with open(file_path.replace(".json", "_power_lib_empty.json"), "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def import_power_lib(self, file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.loads(f.read())
        for _, scfg in self.power_configs.items():
            for node_name, i_comp in scfg.i_comp.items():
                if i_comp.part_name not in data:
                    continue
                for name, props in data[i_comp.part_name].items():
                    if not len(set(i_comp.pin_list.split("-")).difference(props["pin_list"].split("-"))):
                        i_comp.value = props["value"]
                        i_comp.power_name = name

    def custom_comp_overwrite(self):
        for _, scfg in self.power_configs.items():
            for node_name, i_comp in scfg.i_comp.items():
                if i_comp.refdes not in self.custom_comps:
                    continue
                for name, props in self.custom_comps[i_comp.refdes].items():
                    if not len(set(str(i_comp.pin_list).split("-")).difference(str(props["pin_list"]).split("-"))):
                        i_comp.value = props["value"]
                        i_comp.power_name = name

    def export_config_excel(self, file_path):
        data = self._get_cfg_dict()

        basic_info = {key: value for key, value in data.items() if not isinstance(value, (list, dict))}
        removal_list = data["removal_list"]
        custom_comps = data["custom_comps"]
        power_config = data["power_configs"]

        with pd.ExcelWriter(file_path) as writer:
            basic = pd.Series(basic_info)
            basic.to_excel(writer, sheet_name='Basic_info', header=False)

            removal_ser = pd.Series(removal_list)
            removal_ser.to_excel(writer, sheet_name="removal_list", header=False)

            for pname, props in power_config.items():

                v_comp = props["v_comp"]
                i_comp = props["i_comp"]

                power_df = None
                for comp_name, comp_props in v_comp.items():
                    if not isinstance(power_df, pd.DataFrame):
                        power_df = pd.DataFrame(comp_props, index=[comp_name])
                    else:
                        #power_df = power_df.append(pd.DataFrame(comp_props, index=[comp_name]))
                        new_df = pd.DataFrame(comp_props, index=[comp_name])
                        power_df = pd.concat([power_df, new_df])

                for comp_name, comp_props in i_comp.items():
                    if not isinstance(power_df, pd.DataFrame):
                        power_df = pd.DataFrame(comp_props, index=[comp_name])
                    else:
                        #power_df = power_df.append(pd.DataFrame(comp_props, index=[comp_name]))
                        new_df = pd.DataFrame(comp_props, index=[comp_name])
                        power_df = pd.concat([power_df, new_df])
                power_df.to_excel(writer, sheet_name=pname)

            custom_comps_df = None
            i = 1
            for refdes, props in custom_comps.items():
                temp = {"refdes": refdes}
                for pname, cp in props.items():
                    temp["power_name"] = pname
                    temp.update(cp)

                    if not custom_comps_df:
                        custom_comps_df = pd.DataFrame(temp, index=[str(i)])
                    else:
                        new_df = pd.DataFrame(temp, index=[str(i)])
                        custom_comps_df = pd.concat([custom_comps_df, new_df])

                    i = i + 1
            if len(custom_comps_df):
                custom_comps_df.to_excel(writer, sheet_name="custom_comps")

    def import_config_excel(self, file_path):
        xls = pd.ExcelFile(file_path)
        for sheet_name in xls.sheet_names:
            df = pd.read_excel(xls, sheet_name=sheet_name, header=None).fillna("")
            if sheet_name.lower() == "basic_info":
                for i in df.values:
                    self.__dict__[i[0]] = i[1]
            elif sheet_name.lower() == "removal_list":
                for i in df.values:
                    self.__dict__[sheet_name.lower()].append(i[1])
            elif sheet_name.lower() == "custom_comps":
                df = pd.read_excel(xls, sheet_name=sheet_name).fillna("")
                for _, i in df.iterrows():
                    self.__dict__[sheet_name.lower()][i.refdes] = {i.power_name: {
                        "pin_list": i.pin_list,
                        "value": i.value}}
            elif sheet_name.lower() == "vrm":
                df = pd.read_excel(xls, sheet_name=sheet_name, index_col=0).fillna("")

                for idx, i in df.iterrows():
                    data = {"v_comp": {}}
                    data["v_comp"][idx] = dict(i)
                    sp = SinglePowerConfig()
                    sp.import_dict(data)
                    self.power_configs[idx] = sp
        return
