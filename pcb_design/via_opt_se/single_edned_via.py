import os
import numpy as np
from pyaedt import Edb
from pyaedt import Hfss3dLayout
from pyaedt.generic.general_methods import generate_unique_folder_name, generate_unique_name


class ViaToplogy:

    def __init__(self,
                 fpath_stackup,
                 layer_signal_1,
                 layer_signal_2,
                 drill_hole_size=300e-6,
                 pad_size=500e-6):

        MODEL_SIZE_X = 6e-3
        MODEL_SIZE_Y = 6e-3
        VIA_NUM_SIZE = 12
        MAX_ARC_POINTS = 16

        aedb_path = os.path.join(generate_unique_folder_name(),
                                      generate_unique_name("11_single_ended_via") + ".aedb")

        self.edbapp = Edb(aedb_path)

        self.edbapp.stackup.import_stackup(fpath_stackup)

        self.edbapp.add_design_variable("$antipaddiam", "0.7mm")
        self.edbapp.add_design_variable("$via_distance", "1mm")
        self.edbapp.add_design_variable("$width_1", "0.115mm")
        self.edbapp.add_design_variable("$width_2", "0.095mm")
        self.edbapp.add_design_variable("$clearance_1", "0.1mm")
        self.edbapp.add_design_variable("$clearance_2", "0.1mm")

        self.edbapp.core_padstack.create_padstack(
            padstackname="VIA", holediam=drill_hole_size, antipaddiam="$antipaddiam", paddiam=pad_size
        )

        self.edbapp.core_padstack.place_padstack([0, 0],
                                                 "VIA",
                                                 net_name="SIG",
                                                 )

        for i in np.arange(0, 360, 30):
            if i in [90, 270]:
                continue
            i_rad = i / 180 * np.pi
            xloc = "{}*{}".format(np.cos(i_rad), "$via_distance")
            yloc = "{}*{}".format(np.sin(i_rad), "$via_distance")
            self.edbapp.core_padstack.place_padstack([xloc, yloc], "VIA", net_name="GND")

        trace_1_path = [[0, 0], [0, self.MODEL_SIZE_Y / 2]]
        poly = self.edbapp.core_primitives.create_trace(trace_1_path,
                                                        layer_name=layer_signal_1,
                                                        width="$width_1",
                                                        net_name="SIG",
                                                        end_cap_style="Flat"
                                                        )
        self.edbapp.core_hfss.create_edge_port_vertical(poly.GetId(), [0, self.MODEL_SIZE_Y / 2], "port_1")

        trace_2_path = [[0, 0], [0, self.MODEL_SIZE_Y / -2]]
        poly = self.edbapp.core_primitives.create_trace(trace_2_path,
                                                        layer_name=layer_signal_2,
                                                        width="$width_2",
                                                        net_name="SIG",
                                                        end_cap_style="Flat"
                                                        )
        self.edbapp.core_hfss.create_edge_port_vertical(poly.GetId(), [0, self.MODEL_SIZE_Y / -2], "port_2")

        # Create ground plane on every layer
        for i in self.edbapp.stackup.stackup_layers.keys():
            prim = self.edbapp.core_primitives.create_rectangle(i,
                                                                "GND",
                                                                representation_type="CenterWidthHeight",
                                                                center_point=[0, 0],
                                                                width=self.MODEL_SIZE_X,
                                                                height=self.MODEL_SIZE_Y
                                                                )
            if i == layer_signal_1:
                poly_void = self.edbapp.core_primitives.create_trace(trace_1_path,
                                                                     layer_name=layer_signal_1,
                                                                     net_name="gnd",
                                                                     width="{}+2*{}".format("$width_1",
                                                                                            "$clearance_1"),
                                                                     start_cap_style="Flat",
                                                                     end_cap_style="Flat")
                self.edbapp.core_primitives.add_void(prim, poly_void)
            elif i == layer_signal_2:
                poly_void = self.edbapp.core_primitives.create_trace(trace_2_path,
                                                                     layer_name=layer_signal_2,
                                                                     net_name="gnd",
                                                                     width="{}+2*{}".format("$width_2",
                                                                                            "$clearance_2"),
                                                                     start_cap_style="Flat",
                                                                     end_cap_style="Flat")
                self.edbapp.core_primitives.add_void(prim, poly_void)

        self.edbapp.save_edb()
        self.edbapp.close_edb()
        self.h3d = Hfss3dLayout(projectname=os.path.join(aedb_path, "edb.def"), specified_version=self.VERSION,
                           non_graphical=False)

        for p in self.h3d.boundaries:
            p["HFSS Type"] = "Wave"
            p["Horizontal Extent Factor"] = str(8)
            p["PEC Launch Width"] = "0.02mm"

            if p.name == "port_1":
                p["Vertical Extent Factor"] = str(8)
                p["PEC Launch Width"] = "0.02mm"
        self.setup = self.h3d.create_setup()
        self.h3d.create_linear_step_sweep(
            self.setup.name,
            "GHz",
            freqstart=0.1,
            freqstop=40,
            step_size=0.1,
            sweepname="sweep1",
            sweep_type="Interpolating",
            interpolation_tol_percent=1,
            interpolation_max_solutions=255,
            save_fields=False,
            use_q3d_for_dc=False,
        )

    def import_setup(self, fpath):
        self.setup.import_from_json(fpath)

    def save_aedt_as(self, fpath):
        if os.path.isfile(fpath):
            os.remove(fpath)
        self.h3d.save_project(fpath)
        self.h3d.close_project()
        self.h3d.release_desktop()


if __name__ == '__main__':
    app = ViaToplogy(fpath_stackup=r"design_docs\stackup_8_layers.csv",
                          layer_signal_1="TOP",
                          layer_signal_2="L6")
    app.import_setup(r"design_docs\hfss3dlayout_my_setup.json")
    app.save_aedt_as(r"C:\Users\hzhou\Downloads\_from_pyaedt\11_single_ended_via.aedt")
