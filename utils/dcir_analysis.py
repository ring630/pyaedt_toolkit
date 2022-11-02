import os
import shutil
from . import log_info

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

    def remove_irrelevant_nets(self, edbapp):
        _nets = [i for i in self.edbapp.core_nets.nets if i not in self.dcir_config.all_power_nets]
        _nets.remove(self.gnd)
        edbapp.core_nets.delete_nets(_nets)

    def remove_gnd(self, edbapp):
        edbapp.core_nets.delete_nets(self.gnd)

    def config_edb(self, remove_irrelevant_nets=True, remove_gnd=False):
        log_info("Loading EDB")
        self.edbapp = Edb(self.edb_name, self.edb_version)

        if remove_irrelevant_nets:
            log_info("Removing irrelevant nets")
            self.remove_irrelevant_nets(self.edbapp)
        if remove_gnd:
            log_info("Removing ground")
            self.remove_gnd(self.edbapp)

        if self.fname_comp_definition:
            self.edbapp.core_components.import_definition(self.fname_comp_definition)

        log_info("Assigning sinks and sources.")
        comp_gnd_pg_name = {}
        for _, single_cfg in self.dcir_config.power_configs.items():
            for node_name, vcomp in single_cfg.v_comp.items():
                pg_gnd = "{}_{}".format(vcomp.refdes, self.gnd)
                if not pg_gnd in list(comp_gnd_pg_name.values()):
                    self.edbapp.core_siwave.create_pin_group_on_net(
                        vcomp.refdes,
                        self.gnd,
                        pg_gnd,
                    )
                    comp_gnd_pg_name[vcomp.refdes] = pg_gnd

                self.edbapp.core_siwave.create_pin_group(
                    vcomp.refdes,
                    vcomp.pin_list.split("-"),
                    node_name
                )
                self.edbapp.core_siwave.create_voltage_source_on_pin_group(
                    node_name,
                    pg_gnd,
                    vcomp.value,
                )

            for node_name, icomp in single_cfg.i_comp.items():
                pg_gnd = "{}_{}".format(icomp.refdes, self.gnd)
                if not pg_gnd in list(comp_gnd_pg_name.values()):
                    self.edbapp.core_siwave.create_pin_group_on_net(
                        icomp.refdes,
                        self.gnd,
                        pg_gnd,
                    )
                    comp_gnd_pg_name[icomp.refdes] = pg_gnd

                self.edbapp.core_siwave.create_pin_group(
                    icomp.refdes,
                    icomp.pin_list.split("-"),
                    node_name
                )
                self.edbapp.core_siwave.create_current_source_on_pin_group(
                    node_name,
                    pg_gnd,
                    icomp.value,
                )
        self.edbapp.core_siwave.add_siwave_dc_analysis()
        self.fpath_result_edb = os.path.join(self.output_folder, self.edb_name)

        self.edbapp.save_edb_as(self.fpath_result_edb)
        self.edbapp.close_edb()

        self.create_aedt()

    def create_aedt(self):
        log_info("Creating aedt project.")
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
