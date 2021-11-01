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

    @property
    def id(self):
        return "{}-{}".format(self.refdes, self.net_name)

    def __init__(self, refdes, net_name, pins=None, part_name=None):
        self.refdes = refdes
        self.net_name = net_name
        self.pins = pins
        self.part_name = part_name


class Sink(Component):

    def __init__(self, refdes, net_name, pins=None, part_name=None, current=0):
        super().__init__(refdes, net_name, pins, part_name)
        self.current = current
        self.net_name = net_name
        self.part_name = part_name
        self.pins = pins

        self.pos_voltage = 0
        self.neg_voltage = 0
        self.voltage = 0

    def add_result(self, pos_voltage, neg_voltage):
        self.pos_voltage = float(pos_voltage)
        self.neg_voltage = float(neg_voltage)
        self.voltage = float(pos_voltage) - float(neg_voltage)


class Source(Component):

    def __init__(self, refdes, net_name, pins=None, part_name=None):
        super().__init__(refdes, net_name, pins, part_name)
        self.refdes = refdes
        self.net_name = net_name
        self.part_name = part_name
        self.pins = pins


class PowerTreeConfig:

    @property
    def id(self):
        return "{}-{}".format(self.source.refdes, self.source.net_name)

    @property
    def nets(self):
        nets = [self.source.net_name]
        for i in self.sinks:
            nets.append(i.net_name)
        return nets

    def __init__(self, voltage, ref_net):
        self.voltage = voltage
        self.source = None
        self.ref_net = ref_net
        self.sinks = []

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

    def __init__(self, layout_file_path, edb_version):
        self.edb_version = edb_version
        self.layout_file_path = layout_file_path

        self.h3d = None

        start = time.time()
        self.appedb = Edb(edbpath=self.layout_file_path,
                          edbversion=self.edb_version)

        edb_components = self.appedb.core_components.components
        edb_nets = self.appedb.core_nets.nets

        if not len(edb_nets):
            raise Exception("No net exists in the design. Initialization failed. Please check edb file name")
        elif not len(edb_components):
            raise Exception("No component exists in the design. Initialization failed. Please check edb file name")
        else:
            print("{} components\n{} nets".format(len(edb_components), len(edb_nets)))
            timer(start, "initialization finished.")

    def close_edb(self):
        self.appedb.close_edb()

    def get_nets_between_components(self, refdes_1, refdes_2):

        comp_1_nets = self.appedb.core_components.get_component_net_connection_info(refdes_1)
        comp_2_nets = self.appedb.core_components.get_component_net_connection_info(refdes_2)
        net_intersection = set(comp_1_nets["net_name"]).intersection(set(comp_2_nets["net_name"]))

        if len(net_intersection) == 1:
            return list(net_intersection)[0]
        else:
            return list(net_intersection)

    def extract_power_tree(self, src_refdes, src_o_net_name, voltage, ref_net_name="GND"):
        print("Extracting {}-{}".format(src_refdes, src_o_net_name))
        powertree_cfg = PowerTreeConfig(voltage, ref_net_name)
        start = time.time()

        powertree_list, columns, net_group = self.appedb.core_nets.get_powertree(src_o_net_name,
                                                                                 [ref_net_name]
                                                                                 )
        # powertree_list.keys =
        # ["refdes", "pin_name", "net_name", "component_type", "component_partname", "pin_list"]

        for comp in powertree_list:
            refdes = comp[columns.index("refdes")]
            pin_name = comp[columns.index("pin_name")]
            net_name = comp[columns.index("net_name")]
            component_type = comp[columns.index("component_type")]
            component_partname = comp[columns.index("component_partname")]
            pin_list = comp[columns.index("pin_list")]

            if component_type in ["IO", "IC", "Other"]:
                data = self.appedb.core_components.get_component_net_connection_info(refdes)
                if not ref_net_name in data["net_name"]:
                    print(comp[columns.index("refdes")], " is not connected to ref net. Excluded")

                elif refdes == src_refdes:
                    src = Source(src_refdes, src_o_net_name, pin_list, component_partname)
                    powertree_cfg.source = src
                else:
                    sink = Sink(refdes, net_name, pin_list, component_partname)

                    if not sink.id in [i.id for i in powertree_cfg.sinks]:
                        powertree_cfg.sinks.append(sink)

        return powertree_cfg

    def config_dcir(self, power_tree_cfg):

        ref_net = power_tree_cfg["ref_net"]
        voltage = power_tree_cfg["voltage"]
        source = power_tree_cfg["source"][0]
        refdes = source["refdes"]
        o_net = source["net_name"]
        source_id = "{}-{}".format(refdes, o_net)

        self.appedb.core_siwave.create_voltage_source_on_net(positive_component_name=refdes,
                                                             positive_net_name=o_net,
                                                             negative_component_name=refdes,
                                                             negative_net_name=ref_net,
                                                             voltage_value=float(voltage),
                                                             phase_value=0,
                                                             source_name=source_id
                                                             )

        for sink in power_tree_cfg["sink"]:
            sink_id = "{}-{}".format(sink["refdes"], sink["net_name"])
            self.appedb.core_siwave.create_current_source_on_net(positive_component_name=sink["refdes"],
                                                                 positive_net_name=sink["net_name"],
                                                                 negative_component_name=sink["refdes"],
                                                                 negative_net_name=ref_net,
                                                                 current_value=float(sink["current"]),
                                                                 phase_value=0,
                                                                 source_name=sink_id)

    def add_siwave_dc_analysis(self, name, node_to_ground, accuracy_level):
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
