import clr
import os
from datetime import datetime
import time
import shutil
import json
import pandas as pd

clr.AddReference('System.Xml')

from pyaedt.edb import Edb
from pyaedt.desktop import Desktop
from pyaedt.hfss3dlayout import Hfss3dLayout


def timer(start, string_text=""):
    print("{}. Elapsed time = {} seconds".format(string_text, round(time.time() - start, 1)))


class Component:

    def __init__(self, part_name=""):
        self.part_name = part_name
        self.power_rails = {}

    def add_power_rail(self, name, pins, current):
        self.power_rails[name] = {"pins": pins,
                                  "current": current}


class Library:

    def __init__(self):
        self.components = {}

    def add_component(self, component=Component()):
        self.components[component.part_name] = component

    def get_current(self, part_name, power_rail_name):
        if power_rail_name:
            return self.components[part_name].power_rails[power_rail_name]["current"]
        return False

    def get_power_rail_name_from_pins(self, part_name, pins):
        for name, i in self.components[part_name].power_rails.items():
            if not i["pins"] == pins:
                continue
            else:
                return name
        return False

    def create_example_library(self, path=""):

        comp = Component("IPD031-201")
        comp.add_power_rail("Core_1V0", "Y14-AB14-AD14-V14-Y20-Y18-Y16-AB20-AB18-T18-V20-V18-V16", 10)
        self.components["IPD031-201"] = comp

        comp = Component("E17764-001")
        comp.add_power_rail("P1V0", "10", 1)
        self.components["E17764-001"] = comp

        self.export_library(path, backup=True)

    def export_library(self, path="", file_name="library.json", backup=False, backup_dir="log"):
        exp = {}
        for part_name, comp in self.components.items():
            exp[part_name] = comp.__dict__

        fpath = os.path.join(path, file_name)
        if os.path.isfile(fpath):
            if backup:
                if not os.path.isdir(backup_dir):
                    os.mkdir(backup_dir)
                current_time = datetime.now().strftime("%y%m%d-%H-%M-%S")
                shutil.copyfile(fpath, os.path.join(backup_dir, "{}-{}".format(fpath, current_time)))

        with open(fpath, "w", encoding="utf-8") as f:
            f.write(json.dumps(exp, indent=4))

    def import_library(self, path="", file_name="library.json"):
        self.components = {}
        with open(os.path.join(path, file_name), "r") as f:
            json_obj = json.load(f)
            for part_name, comp in json_obj.items():
                comp_tmp = Component()
                for k, v in comp.items():
                    comp_tmp.__dict__[k] = v
                self.components[part_name] = comp_tmp
        return


class Sink:

    @property
    def sink_id(self):
        return "{}-{}".format(self.refdes, self.net_name)

    def __init__(self, refdes, net_name, part_name, pins, current=0, comp_type=""):
        self.refdes = refdes
        self.current = current
        self.net_name = net_name
        self.part_name = part_name
        self.pins = pins
        self.comp_type = comp_type

        self.pos_voltage = 0
        self.neg_voltage = 0
        self.voltage = 0

    def add_result(self, pos_voltage, neg_voltage):
        self.pos_voltage = float(pos_voltage)
        self.neg_voltage = float(neg_voltage)
        self.voltage = float(pos_voltage) - float(neg_voltage)


class Source:

    def __init__(self, refdes="", voltage="", output_net_name="", output_inductor_refdes=""):
        self.refdes = refdes
        self.voltage = voltage
        self.output_net_name = output_net_name
        self.output_inductor_refdes = output_inductor_refdes
        self.power_net_name = ""


class UserConfiguration:

    def __init__(self, source=Source()):
        """

        :param source:
        :type source:
        """

        self.reference_net_name = None
        self.node_to_ground = None
        self.source_cfg = []
        if isinstance(source, list):
            self.source_cfg.extend(source)
        else:
            self.source_cfg.append(source)

    def load_project_cfg(self):
        pass

    def load_dcir_cfg(self, path=""):
        """

        :return:
        :rtype:
        """

        with open(os.path.join(path, "configuration.json"), "r") as f:
            json_obj = dict(json.load(f))
            self.reference_net_name = json_obj["project_config"]["reference_net_name"]
            self.source_cfg = json_obj

            # for _, v in json_obj.items():
            # v.output_net_name = v.output_net_name.replace(" ", "")
            # v.output_inductor_refdes = v.output_inductor_refdes.replace(" ", "")
            # self.source_cfg.append(v)

        return True if len(self.source_cfg) else False

    def create_default_config_file(self, path="", backup_dir="log"):
        """

        :return:
        :rtype:
        """
        config_template = {
            "project_config":
                {
                    "reference_net_name": "GND",
                    "node_to_ground": "U3A1"
                },

            "sources": [
                {
                    "refdes": "U3A1",
                    "voltage": 1,
                    "output_net_name": "BST_V1P0_S0",
                    "output_inductor_refdes": "",
                },
                {
                    "refdes": "U3A1",
                    "voltage": 3.3,
                    "output_net_name": "",
                    "output_inductor_refdes": "L3A1",
                }
            ]
        }

        json_obj = json.dumps(config_template, indent=4)
        fpath = os.path.join(path, "configuration.json")
        if os.path.isfile(fpath):
            if not os.path.isdir(backup_dir):
                os.mkdir(backup_dir)

            current_time = datetime.now().strftime("%y%m%d-%H-%M-%S")
            shutil.copyfile(fpath, os.path.join(backup_dir,"{}-{}".format(fpath, current_time)))

        with open(fpath, "w", encoding='utf-8') as f:
            f.write(json_obj)

        return True if os.path.isfile(fpath) else False


class SinkSourceCfg(Source):

    @property
    def cfg_id(self):
        return "{}-{}-{}".format(self.refdes, self.output_net_name, self.output_inductor_refdes)

    def __init__(self, refdes="", voltage="", part_name="", output_net_name="", output_inductor_refdes=""):
        super(SinkSourceCfg, self).__init__(refdes, voltage, output_net_name, output_inductor_refdes)
        self.part_name = part_name
        self.net_group = []
        self.sinks = {}

    def add_sink(self, sink_class):
        if not isinstance(sink_class, Sink):
            print("{} is not an instance of class Sink".format(sink_class))
            raise
        self.sinks[sink_class.sink_id] = sink_class

    def add_rlc(self):
        pass

    def to_json(self, path, display=False):
        tmp = {"powertree_id": self.cfg_id,
               "vrm_refdes": self.refdes,
               "voltage": self.voltage,
               "sinks": []
               }
        for sink in self.sinks.values():
            tmp["sinks"].append(sink.__dict__)

        json_obj = json.dumps(tmp, indent=4)

        with open(os.path.join(path, self.cfg_id + ".json"), "w", encoding="utf-8") as f:
            f.write(json_obj)

        if display:
            print(json_obj)


class CorePowerTree:

    def __init__(self, layout_file_path, edb_version, cfg=UserConfiguration()):
        self.edb_version = edb_version
        self.layout_file_path = layout_file_path

        self._cfg = cfg
        """ansysem_root_dir = os.environ[self.ANSYSEM_ROOT[self.edbversion]]
        self.anstranslator = os.path.join(ansysem_root_dir, "anstranslator.exe")
        # self.pathToSIwaveNg = os.path.join(ansysem_root_dir, "siwave_ng.exe")"""
        self.h3d = None

    def init_edb(self):
        start = time.time()
        self.appedb = Edb(edbpath=self.layout_file_path,
                          edbversion=self.edb_version)

        edb_components = self.appedb.core_components.components
        edb_nets = self.appedb.core_nets.nets

        if not len(edb_nets):
            print(self._cfg.layout_file_path)
            raise Exception("No net exists in the design. Initialization failed. Please check edb file name")
        elif not len(edb_components):
            raise Exception("No component exists in the design. Initialization failed. Please check edb file name")
        else:
            print("{} components\n{} nets".format(len(edb_components), len(edb_nets)))
            timer(start, "initialization finished.")
            return True

    def close_edb(self):
        self.appedb.close_edb()

    def _find_vrm_output_net_name_from_inductor_refdes(self, sink_source_cfg=SinkSourceCfg()):

        if not isinstance(sink_source_cfg, SinkSourceCfg):
            print("{} is not an instance of class SinkSourceCfg".format(sink_source_cfg))

        if not sink_source_cfg.output_inductor_refdes:
            return

        vrm_net_connection = self.appedb.core_components.get_component_net_connection_info(sink_source_cfg.refdes)
        inductor_net_connection = self.appedb.core_components.get_component_net_connection_info(
            sink_source_cfg.output_inductor_refdes)
        net_intersection = set(vrm_net_connection["net_name"]).intersection(set(inductor_net_connection["net_name"]))
        if not len(net_intersection):
            print("Inductor {1} is not connected to VRM {0}".format(sink_source_cfg.refdes,
                                                                    sink_source_cfg.output_inductor_refdes))
            raise
        elif len(net_intersection) == 1:
            sink_source_cfg.output_net_name = list(net_intersection)[0]
            print("Found VRM {} output net_name {} ".format(sink_source_cfg.refdes, sink_source_cfg.output_net_name))

        else:
            print("Both sides of inductor {1} are connected to VRM {0}. {2}".format(sink_source_cfg.refdes,
                                                                                    sink_source_cfg.output_inductor_refdes,
                                                                                    net_intersection))
            raise

    def extract_power_tree(self, sink_source_cfg=SinkSourceCfg(), ref_net_name="GND"):
        if not isinstance(sink_source_cfg, SinkSourceCfg):
            print("{} is not an instance of class SinkSourceCfg".format(sink_source_cfg))

        start = time.time()

        print("Extracting {}".format(sink_source_cfg.cfg_id))
        self._find_vrm_output_net_name_from_inductor_refdes(sink_source_cfg)

        powertree_list, columns, net_group = self.appedb.core_nets.get_powertree(sink_source_cfg.output_net_name,
                                                                                 [ref_net_name])
        # ["refdes", "pin_name", "net_name", "component_type", "component_partname", "pin_list"]
        sink_source_cfg.net_group.extend(net_group)

        for comp in powertree_list:
            if comp[columns.index("component_type")] in ["IO", "IC", "Other"]:
                if comp[columns.index("refdes")] == sink_source_cfg.refdes:
                    continue

                data = self.appedb.core_components.get_component_net_connection_info(comp[columns.index("refdes")])
                if not ref_net_name in data["net_name"]:
                    print(comp[columns.index("refdes")], " is not connected to ref net")
                    continue

                s = Sink(refdes=comp[columns.index("refdes")],
                         net_name=comp[columns.index("net_name")],
                         part_name=comp[columns.index("component_partname")],
                         pins=comp[columns.index("pin_list")],
                         comp_type=comp[columns.index("component_type")],
                         )
                if not s.sink_id in sink_source_cfg.sinks:
                    sink_source_cfg.add_sink(s)
            else:
                # TBD implemented
                sink_source_cfg.add_rlc()

    def power_tree_cleaning(self):
        for powertree_id, complist in self.POWER_TREE.items():
            droplist = []
            for label, row in complist.iterrows():
                data = self.appedb.core_components.get_component_net_connection_info(row.refdes)
                if not self.REF_NET in data["net_name"]:
                    droplist.append(label)
            self.POWER_TREE[powertree_id] = complist.drop(droplist)

    def config_dcir(self, cfg=SinkSourceCfg(), ref_net_name="GND"):

        self.appedb.core_siwave.create_voltage_source_on_net(positive_component_name=cfg.refdes,
                                                             positive_net_name=cfg.output_net_name,
                                                             negative_component_name=cfg.refdes,
                                                             negative_net_name=ref_net_name,
                                                             voltage_value=float(cfg.voltage),
                                                             phase_value=0,
                                                             source_name=cfg.cfg_id
                                                             )

        for sink_id, sink in cfg.sinks.items():
            self.appedb.core_siwave.create_current_source_on_net(positive_component_name=sink.refdes,
                                                                 positive_net_name=sink.net_name,
                                                                 negative_component_name=sink.refdes,
                                                                 negative_net_name=ref_net_name,
                                                                 current_value=float(sink.current),
                                                                 phase_value=0,
                                                                 source_name=sink_id)

    def add_siwave_dc_analysis(self, name, accuracy_level, node_to_ground):
        settings = self.appedb.core_siwave.get_siwave_dc_setup_template()
        settings.accuracy_level = accuracy_level
        settings.name = name
        settings.neg_term_to_ground = node_to_ground
        return self.appedb.core_siwave.add_siwave_dc_analysis(settings)

    def cutout(self, ref_net_name="GND", signal_list=[]):

        self.appedb.create_cutout(signal_list=signal_list, reference_list=[ref_net_name],
                                  extent_type="Conforming", expansion_size=0.01)

    def save_edb_as(self, newloc):

        """        settings = self.edb.core_siwave.get_siwave_dc_setup_template()
        settings.name = "DC_setup"
        settings.neg_term_to_ground = neg_term_list
        self.add_siwave_dc_analysis(settings)"""

        self.appedb._db.SaveAs(newloc)
        self.close_edb()

    def create_aedt_project(self, aedb_path, DCIR_setup_name="DCIR_setup", solve=False):

        aedt = aedb_path.replace(".aedb", ".aedt")
        if os.path.isfile(aedt):
            os.remove(aedt)

        NonGraphical = True
        NewThread = False

        Desktop(self.edb_version, NonGraphical, NewThread)

        targetfile = os.path.join(aedb_path, "edb.def")
        self.h3d = Hfss3dLayout(targetfile)

        if solve:
            start = time.time()

            self.h3d.analyze_setup(DCIR_setup_name)
            print("DCIR Done")

            timer(start, "Simulation is finished.")
        self.h3d.close_project()

    def load_result(self, edb_name, path=""):
        ced_path = os.path.join(path,
                                edb_name + ".aedtresults",
                                edb_name,
                                "DV3_S2_V0",
                                edb_name + ".ced",
                                )
        with open(ced_path, "r") as f:
            text = f.readlines()

        tmp_dict = {}
        for line in text:
            line = line.replace("\n", "").replace("\"", "").split(" ")
            if line[-1] == "I":
                tmp_dict[line[0]] = line

        cols = ["comp_id", "net_name", "pos_voltage", "ref_net_name", "neg_voltage",
                "parallel_R_current", "comp_type"]
        return cols, tmp_dict


if __name__ == "__main__":
    app_powertree = CorePowerTree()
    app_powertree.init_edb()
