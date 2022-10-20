import os
from .dcir_power_tree import DCIRPowerTree
from .edb_preprocessing import LayoutPreProcess
from pyaedt import Edb, Hfss3dLayout, generate_unique_name


class PowerTreeEdb(DCIRPowerTree):

    def __init__(self, fpath, edb_version="2022.2"):
        self.edb_path = fpath
        self.aedb_fpath = os.path.join(r"C:\Users\hzhou\Downloads\_from_pyaedt", generate_unique_name("powertree")+
                                       ".aedb")

        self.appedb = Edb(fpath, edbversion=edb_version)

        DCIRPowerTree.__init__(self, self.appedb, edb_version)

    def load_bom(self, bom_file):
        self.appedb.core_components.import_bom(bom_file, delimiter=",")

    def aedt_def_fpath(self):
        return os.path.join(self.aedb_fpath, "edb.def")

    def aedt_fpath(self):
        return self.aedb_fpath.replace(".aedb", ".aedt")

    def setup_dcir(self):
        for cfg in self.dcir_config_list:
            voltage = cfg.voltage
            source_refdes = cfg.source_refdes
            source_net_name = cfg.source_net_name
            source_name = cfg._node_name

            self.appedb.core_siwave.create_voltage_source_on_net(
                source_refdes, source_net_name, None, None, voltage, 0, source_name
            )
            for sink_name, sink_cfg in cfg.sinks.items():
                current = sink_cfg.current
                sink_net_name = sink_cfg.net_name
                sink_refdes = sink_cfg.refdes
                self.appedb.core_siwave.create_current_source_on_net(
                    sink_refdes, sink_net_name, None, None, current, 0, sink_name
                )
        self.appedb.core_siwave.add_siwave_dc_analysis()
        self.save_edb()

    def save_edb(self):
        self.appedb.save_edb_as(self.aedb_fpath)
        self.appedb.close_edb()

    def analyze(self):
        app_3dl = Hfss3dLayout(self.aedt_def_fpath(), specified_version="2022.2")
        app_3dl.analyze_nominal()
        app_3dl.save_project(self.aedt_fpath())
        app_3dl.close_desktop()
        app_3dl.release_desktop()
