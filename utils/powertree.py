import clr
import os
from datetime import datetime
import time
import shutil

import pandas as pd

clr.AddReference('System.Xml')

from pyaedt.edb import Edb
from pyaedt import Desktop
from pyaedt import Hfss3dLayout


def timer(start, string_text=""):
    print("{}. Elapsed time = {} seconds".format(string_text, round(time.time() - start, 1)))


class PowerTree:
    POWER_TREE = {}  # REFDES-NETNAME: COMP_DICT
    POWER_TREE_RLC = {}  # REFDES-NETNAME: COMP_DICT
    EXCLUDE_COMPONENTS = []
    REF_NET = None
    COMP_WO_CURRENT = None

    EDB_OPEN = False

    ANSYSEM_ROOT = {"2020.1": "ANSYSEM_ROOT201",
                    "2020.2": "ANSYSEM_ROOT202",
                    "2021.1": "ANSYSEM_ROOT211",
                    "2021.2": "ANSYSEM_ROOT212",
                    "2022.1": "ANSYSEM_ROOT221",
                    }

    def __init__(self, project_dir,
                 layout_file_name,
                 local_power_lib_fname=None,
                 edbversion="2021.2"):

        self.project_dir = os.path.abspath(project_dir)
        self.layout_dir = os.path.join(self.project_dir, "layout")
        self.layout_fpath = os.path.join(self.layout_dir, layout_file_name)
        self.config_file = os.path.join(self.project_dir, "config.json")
        self.log_dir = os.path.join(self.project_dir, "log")
        self.result_dir = os.path.join(self.project_dir, "result")
        self.configured_edb_path = os.path.join(self.result_dir, "configured_edb.aedb")
        self.aedt_results_dir = None

        if not os.path.isdir(self.project_dir):
            os.mkdir(self.project_dir)
        if not os.path.isdir(self.layout_dir):
            os.mkdir(self.layout_dir)
        if not os.path.isdir(self.log_dir):
            os.mkdir(self.log_dir)
        if not os.path.isdir(self.result_dir):
            os.mkdir(self.result_dir)
        if not os.path.isdir(self.configured_edb_path):
            os.mkdir(self.configured_edb_path)

        self.edbversion = edbversion
        """ansysem_root_dir = os.environ[self.ANSYSEM_ROOT[self.edbversion]]
        self.anstranslator = os.path.join(ansysem_root_dir, "anstranslator.exe")
        # self.pathToSIwaveNg = os.path.join(ansysem_root_dir, "siwave_ng.exe")"""
        self.h3d = None

        self.local_power_lib_fname = None if not local_power_lib_fname else os.path.join(self.project_dir,
                                                                                         local_power_lib_fname)

    def define_excluded_componenets(self, complist):
        self.EXCLUDE_COMPONENTS = complist

    def define_reference_net(self, reference_net):
        self.REF_NET = reference_net

    def Initialize_EDB(self):
        start = time.time()
        self.edb = Edb(edbpath=self.layout_fpath, edbversion=self.edbversion)
        self.EDB_OPEN = True

        self.edb_components = self.edb.core_components.components
        self.edb_nets = self.edb.core_nets.nets

        if len(self.edb_nets):

            print("{} components\n{} nets".format(len(self.edb_components), len(self.edb_nets)))
            timer(start, "initialization finished.")
        else:
            raise Exception("Initialization failed. Please check edb file path\n")

    def close_edb(self):
        self.edb.close_edb()

    def extract_power_tree(self, vrms):

        for net_name, vrm in vrms.items():
            start = time.time()
            print("Extracting {}".format(net_name))
            vrm_refdes = vrm["VRM_REFDES"]
            power_tree_id = "{}-{}".format(vrm_refdes, net_name)
            voltage = vrm["VOLTAGE"]
            powertree_list, columns, power_nets = self.edb.core_nets.get_powertree(net_name, [self.REF_NET])
            df = pd.DataFrame(powertree_list, columns=columns)

            df = df.drop(df[df.refdes.isin(self.EXCLUDE_COMPONENTS)].index)

            # exclude RLCs
            df_list = []
            df_other = []
            for t, i in df.groupby("component_type"):
                if t == "IO":
                    df_list.append(i)
                elif t == "IC":
                    df_list.append(i)
                elif t == "Other":
                    df_list.append(i)
                else:
                    df_other.append(i)

            df_active_comp = pd.concat(df_list, ignore_index=True)
            df_active_comp = df_active_comp.drop("pin_name", 1)
            df_active_comp = df_active_comp.drop_duplicates()

            # identify sink and source
            df_active_comp["component_type"] = "Sink"
            df_active_comp["voltage"] = " "
            df_active_comp["current"] = " "

            df_active_comp["comp_id"] = df_active_comp["refdes"] + "-" + df_active_comp["net_name"]
            df_active_comp.loc[df_active_comp.comp_id == power_tree_id, ["component_type"]] = "Source"
            df_active_comp.loc[df_active_comp.comp_id == power_tree_id, ["voltage"]] = voltage

            self.POWER_TREE[power_tree_id] = df_active_comp

            # collect RLCs
            df_other_comp = pd.concat(df_other, ignore_index=True)
            df_other_comp = df_other_comp.drop("pin_name", 1)
            df_other_comp = df_other_comp.drop_duplicates()
            self.POWER_TREE_RLC[power_tree_id] = df_other_comp

    def power_tree_cleaning(self):

        for powertree_id, complist in self.POWER_TREE.items():
            droplist = []
            for label, row in complist.iterrows():
                data = self.edb.core_components.get_component_net_connection_info(row.refdes)
                if not self.REF_NET in data["net_name"]:
                    droplist.append(label)
            self.POWER_TREE[powertree_id] = complist.drop(droplist)

    def assign_component_current(self, library_filename=None):
        if not library_filename:
            return

        fpath = os.path.join(self.project_dir, library_filename)
        df = pd.read_csv(fpath, dtype="string")
        df["part_number_id"] = df["component_partname"] + "-" + df["pin_list"]
        for row, lib_comp in df.iterrows():
            for k, i in self.POWER_TREE.items():
                i["part_number_id"] = i["component_partname"] + "-" + i["pin_list"]
                i.loc[i.part_number_id == lib_comp.part_number_id, "current"] = lib_comp.current

    def export_powertree_to_csv(self):

        current_time = datetime.now().strftime("%y%m%d-%H-%M-%S")
        fdir = os.path.join(self.result_dir, current_time)
        os.mkdir(fdir)

        for k, i in self.POWER_TREE.items():
            i.drop(["comp_id", "pin_list", "part_number_id"], 1).to_csv(os.path.join(fdir, k + ".csv"))
        for k, i in self.POWER_TREE_RLC.items():
            i.to_csv(os.path.join(fdir, k + "_RLC.csv"))

    def export_component_wo_current(self):
        df = pd.concat(self.POWER_TREE.values())
        df = df[df["voltage"] != " "]
        df = df[["component_partname", "pin_list", "current"]]
        df = df[df["current"] == " "]
        df.drop_duplicates()
        df.to_csv(os.path.join(self.log_dir, "comp_wo_current.csv"))

    def config_dcir(self, cutout=True):
        neg_term_list = []
        cutout_signal_list = []
        for powertree_id, complist in self.POWER_TREE.items():

            vrm, vrm_netname = powertree_id.split("-")
            # data = self.edb.core_components.get_component_net_connection_info(vrm)
            voltage = complist.loc[complist.component_type == "Source", "voltage"].values[0]
            self.edb.core_siwave.create_voltage_source(positive_component_name=vrm,
                                                       positive_net_name=vrm_netname,
                                                       negative_component_name=vrm,
                                                       negative_net_name=self.REF_NET,
                                                       voltage_value=float(voltage),
                                                       phase_value=0,
                                                       source_name=powertree_id
                                                       )
            neg_term_list.append(powertree_id)
            cutout_signal_list.append(vrm_netname)

            for row, sink in complist[complist.component_type == "Sink"].iterrows():
                refdes, net_name = sink["refdes"], sink["net_name"]
                comp_id = sink["comp_id"]
                self.edb.core_siwave.create_current_source(positive_component_name=refdes,
                                                           positive_net_name=net_name,
                                                           negative_component_name=refdes,
                                                           negative_net_name=self.REF_NET,
                                                           current_value=sink["current"],
                                                           phase_value=0,
                                                           source_name=comp_id)
                cutout_signal_list.append(net_name)

        if cutout:
            self.edb.create_cutout(signal_list=cutout_signal_list, reference_list=[self.REF_NET],
                                   extent_type="Bounding", expansion_size=0.01)

        settings = self.edb.core_siwave.get_siwave_dc_setup_template()
        settings.name = "DC_setup"
        settings.neg_term_to_ground = neg_term_list
        self.add_siwave_dc_analysis(settings)
        self.save_edb_as(self.configured_edb_path)

    def add_siwave_dc_analysis(self, accuracy_level=1):
        return self.edb.core_siwave.add_siwave_dc_analysis(accuracy_level)

    def save_edb(self):
        self.edb.save_edb()

    def save_edb_as(self, newloc):

        self.edb._db.SaveAs(newloc)
        self.close_edb()

    def create_aedt_project(self, solve=False):

        self.aedt_results_dir = self.configured_edb_path.replace(".aedb", ".aedtresults")
        if os.path.isdir(self.aedt_results_dir):
            shutil.rmtree(self.aedt_results_dir)

        aedt = self.configured_edb_path.replace(".aedb", ".aedt")
        if os.path.isfile(aedt):
            os.remove(aedt)

        NonGraphical = True
        NewThread = False

        Desktop(self.edbversion, NonGraphical, NewThread)

        targetfile = os.path.join(self.configured_edb_path, "edb.def")
        self.h3d = Hfss3dLayout(targetfile)

        if solve:
            start = time.time()

            self.h3d.analyze_setup("DC_setup")
            print("DCIR Done")

            timer(start, "Simulation is finished.")
        self.h3d.close_project()

    def load_result(self, fpath=None):
        layout_fpath = os.path.basename(self.layout_fpath).replace(".aedb", "").replace(".brd", "").replace(".tgz", "")
        if not fpath:
            dcir_result_fpath = os.path.join(self.aedt_results_dir,
                                             layout_fpath,
                                             "DV3_S2_V0",
                                             os.path.basename(self.configured_edb_path).replace("aedb", "ced")
                                             )
        else:
            dcir_result_fpath = fpath

        df = pd.read_csv(dcir_result_fpath,
                         names=["comp_id", "net_name", "pos_voltage", "ref_net_name", "neg_voltage",
                                "parallel_R_current", "comp_type"], sep=" ", index_col=False)

        df = df[df.comp_type == "I"]

        for _, complist in self.POWER_TREE.items():
            complist["pos_voltage"] = " "
            complist["neg_voltage"] = " "
            for _, pt_row in complist[complist.component_type == "Sink"].iterrows():
                # c = pt_row.net_name + "_" + pt_row.comp_id
                c = pt_row.comp_id

                for _, row in df.iterrows():
                    comp_id = row.comp_id
                    pos_voltage = row.pos_voltage
                    neg_voltage = row.neg_voltage

                    if c == comp_id:
                        complist.loc[complist.comp_id == pt_row.comp_id, "pos_voltage"] = pos_voltage
                        complist.loc[complist.comp_id == pt_row.comp_id, "neg_voltage"] = neg_voltage
                        complist["voltage_drop"] = pd.to_numeric(complist.pos_voltage,
                                                                 errors="ignore") + -1 * pd.to_numeric(
                            complist.neg_voltage, errors="ignore")
        self.export_powertree_to_csv()


if __name__ == "__main__":
    pass
