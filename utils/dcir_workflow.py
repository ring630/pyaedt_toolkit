from utils.corepowertree import CorePowerTree, UserConfiguration, SinkSourceCfg, Library, Component
from copy import deepcopy as copy
import os
from datetime import datetime

"""
******** User Action *******

Preparation
1, create a project folder under DCIR_Automation and name it. example_project is used as the folder name for example.
2, create folder EDB under project folder
3, copy .aedb folder under EDB folder. edb.def should be in .aedb folder.
4, copy comp_lib_template.csv into project folder and rename it as comp_lib.csv
"""

"""
0: "Only check components on power tree"
1: "Only export DCIR project"
2: "Simulate in Non-graphic mode"
"""


# mode = 1


class DcirWorkflow:

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
    def layout_file_path(self):
        """

        :return:
        :rtype:
        """
        return os.path.join(os.path.abspath(""), "layout_database", self.layout_file_name)

    @property
    def layout_file_basename(self):
        return self.layout_file_name.replace(".aedb", "")

    def __init__(self, edb_version, layout_file_name):
        self.edb_version = edb_version
        self.layout_file_name = layout_file_name

        self.user_configuration = UserConfiguration()
        self.app_power_tree = CorePowerTree(self.layout_file_path, self.edb_version, self.user_configuration)
        self.power_trees = []
        self.library = Library()
        self.library_to_be_filled = Library()

        self.node_to_ground= []

        if not os.path.isdir("log"):
            os.mkdir("log")

    def _load_user_configuration(self):
        self.user_configuration.load_dcir_cfg()

    def _create_power_tree_cfg(self):
        self.app_power_tree.init_edb()
        for vrm in self.user_configuration.source_cfg["sources"]:
            sink_source_cfg = SinkSourceCfg(refdes=vrm["refdes"],
                                voltage=vrm["voltage"],
                                output_net_name=vrm["output_net_name"],
                                output_inductor_refdes=vrm["output_inductor_refdes"])

            if not vrm["output_net_name"]:
                self.app_power_tree._find_vrm_output_net_name_from_inductor_refdes(sink_source_cfg)

            self.power_trees.append(sink_source_cfg)

    def _assign_current_from_library(self):

        for cfg in self.power_trees:
            for sink_id, sink in cfg.sinks.items():
                if sink.part_name in self.library.components:
                    power_rail_name = self.library.get_power_rail_name_from_pins(sink.part_name, sink.pins)
                    if power_rail_name:
                        sink.current = self.library.get_current(part_name=sink.part_name,
                                                                power_rail_name=power_rail_name)
                        continue

                comp = Component(sink.part_name)
                comp.add_power_rail(sink.sink_id, sink.pins, current=0)
                self.library_to_be_filled.add_component(comp)
        self.library_to_be_filled.export_library(file_name="library_to_be_filled.json")

    def _export_library_to_be_filled(self):
        self.library_to_be_filled.export_library(file_name="library_to_be_filled.json")

    def _import_library(self):
        self.library.import_library()

    def _refresh_library(self):
        self.library.import_library()
        self.library_to_be_filled.import_library(file_name="library_to_be_filled.json")
        comp_to_remove = []
        for part_name, comp in self.library_to_be_filled.components.items():
            comp_filled = copy(comp)
            for name, p in comp.power_rails.items():
                if not p["current"]:
                    del comp_filled.power_rails[name]
            if len(comp_filled.power_rails):
                comp_to_remove.append(part_name)
                if part_name in self.library.components:
                    comp_temp = self.library.components[part_name]
                    comp_temp.power_rails = {**comp_temp.power_rails, **comp_filled.power_rails}
                    print("add new power rails to existing component {}".format(part_name))
                else:
                    self.library.add_component(comp_filled)
                    print("add new components {}".format(part_name))

        for i in comp_to_remove:
            del self.library_to_be_filled.components[i]
        self.library_to_be_filled.export_library(file_name="library_to_be_filled.json")
        self.library.export_library()

    def _extract_power_trees(self):
        for cfg in self.power_trees:
            self.app_power_tree.extract_power_tree(cfg, ref_net_name=self.user_configuration.reference_net_name)
            if cfg.refdes == self.user_configuration.node_to_ground:
                self.node_to_ground.append(cfg.cfg_id)

    def _config_dcir(self, DCIR_setup_name="DCIR_setup", path="result", cutout=False, solve=False):
        signal_list = []
        for cfg in self.power_trees:
            self.app_power_tree.config_dcir(cfg, ref_net_name=self.user_configuration.reference_net_name)
            signal_list.extend(cfg.net_group)

        if cutout:
            self.app_power_tree.cutout(self.user_configuration.reference_net_name, signal_list)

        self.app_power_tree.add_siwave_dc_analysis(DCIR_setup_name, node_to_ground=self.node_to_ground,
                                                   accuracy_level=1)

        if not os.path.isdir(path):
            os.mkdir(path)
        aedb_path = os.path.join(path, self.layout_file_name)
        self.app_power_tree.save_edb_as(aedb_path)
        self.app_power_tree.create_aedt_project(aedb_path, DCIR_setup_name=DCIR_setup_name, solve=solve)

    def _wrtie_results_to_json(self, path="result", display=False):
        if not os.path.isdir(path):
            os.mkdir(path)

        current_time = datetime.now().strftime("%y%m%d-%H-%M-%S")
        fpath_w_time = os.path.join(path, current_time)
        os.mkdir(fpath_w_time)
        for ss_cfg in self.power_trees:
            ss_cfg.to_json(fpath_w_time, display=display)
        return fpath_w_time

    def _read_results(self, path="result"):
        cols, result = self.app_power_tree.load_result(edb_name=self.layout_file_basename,
                                            path=path
                                            )
        for ss_cfg in self.power_trees:
            for sink_id, sink in ss_cfg.sinks.items():
                if sink_id in result:
                    pos_voltage = result[sink_id][cols.index("pos_voltage")]
                    neg_voltage = result[sink_id][cols.index("neg_voltage")]
                    sink.add_result(pos_voltage, neg_voltage)

    def extract_power_tree(self):

        self._load_user_configuration()
        self._create_power_tree_cfg()
        self._extract_power_trees()
        self._import_library()

        print("*"*40)
        print("*** Extraction is done. Please to to next step ***")
        print("*" * 40)

    def write_result(self):
        self._wrtie_results_to_json()

    def assign_current_from_library(self):
        self._assign_current_from_library()

    def update_library(self):
        self._refresh_library()

        num = len(self.library_to_be_filled.components)
        print("There are {} components have no current definition".format(num))
        print("Please check file {}".format("library_to_be_filled.json"))

    def analyze(self):
        self._config_dcir(DCIR_setup_name="DCIR_setup", cutout=False, solve=True)
        self._read_results()
        result_folder = self._wrtie_results_to_json()
        print("*" * 40)
        print("*** DCIR analysis is done")
        print("*" * 40)

        print("*** Please see results here {}".format(result_folder))


    def run_all(self):
        self.extract_power_tree()
        self.analyze()
