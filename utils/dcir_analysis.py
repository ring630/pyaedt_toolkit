import os
import shutil
from pyaedt import Desktop, Edb, Hfss3dLayout
from utils.configuration import PowerTreeConfig


class DCIRAnalysis:

    def __init__(self, project_dir, fname_cfg):
        self.default_cwd = os.getcwd()
        os.chdir(project_dir)

        self.dcir_config = PowerTreeConfig(fname_cfg)

        self.gnd = self.dcir_config.gnd_net_name

        self.fname_comp_definition = self.dcir_config.comp_definition

        self.edb_version = str(self.dcir_config.edb_version)
        self.edb_name = self.dcir_config.layout_file_name

        # Create result folder
        self.output_folder = "dcir_ananylsis_result"
        if not os.path.isdir(self.output_folder):
            os.mkdir(self.output_folder)

    def config_edb(self):
        self.edbapp = Edb(self.edb_name, self.edb_version)
        self.edbapp.core_components.import_definition(self.fname_comp_definition)

        for _, single_cfg in self.dcir_config.power_configs.items():
            for node_name, vcomp in single_cfg.v_comp.items():
                self.edbapp.core_siwave.create_voltage_source_on_net(vcomp.refdes,
                                                                     vcomp.net_name,
                                                                     vcomp.refdes,
                                                                     self.gnd,
                                                                     vcomp.value,
                                                                     0,
                                                                     node_name
                                                                     )
            for node_name, icomp in single_cfg.v_comp.items():
                self.edbapp.core_siwave.create_current_source_on_net(icomp.refdes,
                                                                     icomp.net_name,
                                                                     icomp.refdes,
                                                                     self.gnd,
                                                                     icomp.value,
                                                                     0,
                                                                     node_name
                                                                     )
        self.edbapp.core_siwave.add_siwave_dc_analysis()
        self.fpath_result_edb = os.path.join(self.output_folder, self.edb_name)

        self.edbapp.save_edb_as(self.fpath_result_edb)
        self.edbapp.close_edb()

        self.create_aedt()

    def create_aedt(self):
        aedt_path = self.fpath_result_edb.replace(".aedb", ".aedt")
        aedt_result_path = aedt_path.replace("aedt", "aedtresults")
        if os.path.isfile(aedt_path):
            os.remove(aedt_path)
        if os.path.isdir(aedt_result_path):
            shutil.rmtree(aedt_result_path)

        non_graphical = True
        new_thread = True

        desktop = Desktop(self.edb_version, non_graphical, new_thread)
        hfss3dl = Hfss3dLayout(os.path.join(self.fpath_result_edb, "edb.def"))
        hfss3dl.save_project()
        hfss3dl.close_project()
        desktop.release_desktop()
        os.chdir(self.default_cwd)
