from utils.corepowertree import CorePowerTree, PowerTreeConfig, Component
from copy import deepcopy as copy
import os
from datetime import datetime
import json

class DcirAutomation:

    @property
    def ansysem_path(self):
        """

        :return:
        :rtype:
        """
        ANSYSEM_ROOT = {"2020.1": "ANSYSEM_ROOT201",
                        "2020.2": "ANSYSEM_ROOT202",
                        "2021.1": "ANSYSEM_ROOT211",
                        "2021.2": "ANSYSEM_ROOT212",
                        "2022.1": "ANSYSEM_ROOT221",
                        }
        return ANSYSEM_ROOT[self.edb_version]

    @property
    def layout_file_basename(self):
        return self.layout_file_path.replace(".aedb", "")

    def __init__(self,
                 layout_file,
                 edb_version="2021.2",
                 ):

        if not os.path.isdir("log"):
            os.mkdir("log")

        self.layout_file_path = layout_file
        self.edb_version = edb_version

        self.powertree_config = []
        self.powertree_json_path = []

        self.app_power_tree = CorePowerTree(self.layout_file_path, self.edb_version)

    def config_dcir(self, node_to_ground, solve=False, DCIR_setup_name="DCIR_setup"):

        for path in self.powertree_json_path:
            with open(path, "r") as f:
                cfg = json.load(f)
                self.app_power_tree.config_dcir(cfg)

        self.app_power_tree.add_siwave_dc_analysis(DCIR_setup_name, node_to_ground=node_to_ground,
                                                   accuracy_level=1)

        aedb_path = os.path.join(self.layout_file_path.replace(".aedb", "_dcir.aedb"))
        self.app_power_tree.save_edb_as(aedb_path)
        self.app_power_tree.create_aedt_project(aedb_path, DCIR_setup_name=DCIR_setup_name, solve=solve)

    def extract_power_tree(self, sources, ref_net_name="GND"):

        for src in sources:
            src_refdes = src["refdes"]
            voltage = src["voltage"]

            if src["o_net_name"]:
                o_net_name = src["o_net_name"]
            else:
                o_net_name = self.app_power_tree.get_nets_between_components(src_refdes, src["o_inductor_refdes"])

            power_tree_cfg = self.app_power_tree.extract_power_tree(src_refdes, o_net_name, voltage, ref_net_name)
            self.powertree_config.append(power_tree_cfg)

        self._export_power_tree_cfg()

    def _export_power_tree_cfg(self):
        for pt in self.powertree_config:
            tmp = {"id": pt.id,
                   "voltage": pt.voltage,
                   "ref_net": pt.ref_net,
                   "source": [],
                   "sink": []
                   }
            tmp["source"].append(pt.source.__dict__)
            for sink in pt.sinks:
                tmp["sink"].append(sink.__dict__)

            json_obj = json.dumps(tmp, indent=4)

            path = os.path.join(os.path.dirname(self.layout_file_path),pt.id + ".json")
            self.powertree_json_path.append(path)
            with open(path, "w", encoding="utf-8") as f:
                f.write(json_obj)


