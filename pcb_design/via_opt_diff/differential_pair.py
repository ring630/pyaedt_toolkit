import os
from pyaedt import Edb
from pyaedt import Hfss3dLayout


class Bench3DL:

    def __init__(self, work_dir):
        self._work_dir = ""
        if work_dir:
            os.chdir(work_dir)
            self._work_dir = work_dir

        self.x_limit_p = "2mm"
        self.x_limit_n = "-2mm"
        self.y_limit_p = "3mm"
        self.y_limit_n = "-1mm"

        self.appedb = Edb(edbversion="2022.2")

    def _add_default_variables(self):
        variables = {
            "$antipad_size": "1mm",
            "$drill_offset_x": "0mm",
            "$drill_offset_y": "0mm",
            "$etching_tol": "0mm"
        }
        for var, val in variables.items():
            self.appedb.add_design_variable(var, val)

    def _add_default_padstacks(self):
        via_padstacks = {}
        via_padstacks["via_200"] = {"padstackname": "via_200",
                                    "holediam": "250um",
                                    "paddiam": "450um",
                                    "antipaddiam": "$antipad_size+$etching_tol*2",
                                    "antipad_shape": "Circle",
                                    "offset_x": "$drill_offset_x*-1",
                                    "offset_y": "$drill_offset_y*-1",
                                    "has_hole": True,
                                    "pad_offset_x": "$drill_offset_x*-1",
                                    "pad_offset_y": "$drill_offset_y*-1"
                                    }
        via_padstacks["via_250"] = {"padstackname": "via_250",
                                    "holediam": "250um",
                                    "paddiam": "450um",
                                    "antipaddiam": "$antipad_size+$etching_tol*2",
                                    "antipad_shape": "Circle",
                                    "offset_x": "$drill_offset_x*-1",
                                    "offset_y": "$drill_offset_y*-1",
                                    "has_hole": True,
                                    "pad_offset_x": "$drill_offset_x*-1",
                                    "pad_offset_y": "$drill_offset_y*-1"
                                    }
        via_padstacks["via_250_bullet"] = {"padstackname": "via_250_bullet",
                                           "holediam": "250um",
                                           "paddiam": "450um",
                                           "antipad_shape": "Bullet",
                                           "x_size": "$via_distance / 2 +$antipad_size / 2+$etching_tol*2",
                                           "y_size": "$antipad_size+$etching_tol*2",
                                           "corner_radius": "$antipad_size",
                                           "offset_x": "$drill_offset_x*-1",
                                           "offset_y": "$drill_offset_y*-1",
                                           "has_hole": True,
                                           "pad_offset_x": "$drill_offset_x*-1",
                                           "pad_offset_y": "$drill_offset_y*-1"
                                           }

        via_padstacks["bga_400"] = {"padstackname": "bga_400",
                                    "paddiam": "400um",
                                    "has_hole": False
                                    }
        for via_name, props in via_padstacks.items():
            self.appedb.core_padstack.create_padstack(**props)

    def _create_board(self, layer_count=2, dielectric_thickness="100um"):
        self.appedb.stackup.create_symmetric_stackup(layer_count, dielectric_thickness=dielectric_thickness)

        # Create ground plane on every layer
        gnd_planes = {}
        for i in self.appedb.stackup.signal_layers.keys():
            prim = self.appedb.core_primitives.create_rectangle(i,
                                                                "GND",
                                                                representation_type="LowerLeftUpperRight",
                                                                lower_left_point=(self.x_limit_n, self.y_limit_n),
                                                                upper_right_point=(self.x_limit_p, self.y_limit_p)
                                                                )
            gnd_planes[i] = prim

        return gnd_planes

    def _save_edb_and_close(self, aedb_name):
        self.appedb.save_edb_as(aedb_name+".aedb")
        self.appedb.close_edb()

    def _save_as_aedt(self, name):

        h3d = Hfss3dLayout(projectname=name + ".aedb",
                           specified_version="2022.2",
                           non_graphical=True)

        h3d.edit_hfss_extents(air_vertical_positive_padding="10mm",
                              air_vertical_negative_padding="1mm")

        if self._work_dir:
            h3d.save_project(os.path.join(self._work_dir, name) + ".aedt")
        else:
            h3d.save_project(name + ".aedt")
        h3d.release_desktop()


class DiffPairType1:

    def __init__(self, work_dir=None):

        self.name = "diff_pair_type_1"
        self.sig_layers = ("TOP", "L4")
        self.layer_count = 8
        self.dielectric_thickness = "150um"

        self._work_dir = work_dir
        self._gnd_planes = None

    def create(self, save_as_aedt=True):
        pyaedt_edb = Bench3DL(self._work_dir)
        pyaedt_edb.appedb.add_design_variable("$sig_width_0", "0.1mm")
        pyaedt_edb.appedb.add_design_variable("$sig_gap_0", "0.15mm")
        pyaedt_edb.appedb.add_design_variable("$sig_width_1", "0.075mm")
        pyaedt_edb.appedb.add_design_variable("$sig_gap_1", "0.1mm")
        pyaedt_edb.appedb.add_design_variable("$via_distance", "0.8mm")

        # Place pin/via
        data = {
            0: ["GND", "SIG_P", "SIG_N", "GND"]
        }
        pyaedt_edb._gnd_planes = pyaedt_edb._create_board(self.layer_count, self.dielectric_thickness)
        pyaedt_edb._add_default_variables()
        pyaedt_edb._add_default_padstacks()

        pyaedt_edb._gnd_planes[self.sig_layers[0]].delete()
        pyaedt_edb._gnd_planes[self.sig_layers[1]].delete()
        for name, val in pyaedt_edb.appedb.stackup.layers.items():
            if name in self.sig_layers:
                val.color = (255, 255, 0)
                val.transparency = 20
            else:
                val.color = (192, 192, 192)
                val.transparency = 90

        sig_p_0, sig_path_p_0, sig_n_0, sig_path_n_0 = None, None, None, None
        sig_p_1, sig_path_p_1, sig_n_1, sig_path_n_1 = None, None, None, None
        for x, d in data.items():
            for y, net_name in enumerate(d):
                via_x_loc = "$drill_offset_x+{}*$via_distance".format(x)
                via_y_loc = "$drill_offset_y+{}*$via_distance".format(y)
                x_loc = "{}*$via_distance".format(x)
                y_loc = "{}*$via_distance".format(y)

                if net_name.endswith("_P"):
                    x_loc_2 = "{}-{}".format(x_loc, "($via_distance-$sig_gap_0-$sig_width_0)/2")
                    y_loc_2 = "{}+{}".format(y_loc, "($via_distance-$sig_gap_0-$sig_width_0)/2")
                    sig_path_p_0 = [(x_loc, y_loc), (x_loc_2, y_loc_2), (pyaedt_edb.x_limit_n, y_loc_2)]
                    sig_p_0 = pyaedt_edb.appedb.core_primitives.create_trace(
                        sig_path_p_0,
                        layer_name=self.sig_layers[0],
                        width="$sig_width_0",
                        net_name=net_name,
                        end_cap_style="Flat"
                    )
                    x_loc_2 = "{}+{}".format(x_loc, "($via_distance-$sig_gap_1-$sig_width_1)/2")
                    y_loc_2 = "{}+{}".format(y_loc, "($via_distance-$sig_gap_1-$sig_width_1)/2")
                    sig_path_p_1 = [(x_loc, y_loc), (x_loc_2, y_loc_2), (pyaedt_edb.x_limit_p, y_loc_2)]
                    sig_p_1 = pyaedt_edb.appedb.core_primitives.create_trace(
                        sig_path_p_1,
                        layer_name=self.sig_layers[1],
                        width="$sig_width_1",
                        net_name=net_name,
                        end_cap_style="Flat"
                    )
                elif net_name.endswith("_N"):
                    x_loc_2 = "{}-{}".format(x_loc, "($via_distance-$sig_gap_0-$sig_width_0)/2")
                    y_loc_2 = "{}-{}".format(y_loc, "($via_distance-$sig_gap_0-$sig_width_0)/2")
                    sig_path_n_0 = [(x_loc, y_loc), (x_loc_2, y_loc_2), (pyaedt_edb.x_limit_n, y_loc_2)]
                    sig_n_0 = pyaedt_edb.appedb.core_primitives.create_trace(
                        sig_path_n_0,
                        layer_name=self.sig_layers[0],
                        width="$sig_width_0",
                        net_name=net_name,
                        end_cap_style="Flat"
                    )
                    x_loc_2 = "{}+{}".format(x_loc, "($via_distance-$sig_gap_1-$sig_width_1)/2")
                    y_loc_2 = "{}-{}".format(y_loc, "($via_distance-$sig_gap_1-$sig_width_1)/2")
                    sig_path_n_1 = [(x_loc, y_loc), (x_loc_2, y_loc_2), (pyaedt_edb.x_limit_p, y_loc_2)]
                    sig_n_1 = pyaedt_edb.appedb.core_primitives.create_trace(
                        sig_path_n_1,
                        layer_name=self.sig_layers[1],
                        width="$sig_width_1",
                        net_name=net_name,
                        end_cap_style="Flat"
                    )

                pos = [via_x_loc, via_y_loc]
                via = pyaedt_edb.appedb.core_padstack.place_padstack(pos, "via_200", net_name=net_name)
                if not net_name == "GND":
                    layer = self.sig_layers[-1]
                    via.set_backdrill_bottom(layer, 0.5e-3)

        # self.appedb.core_hfss.create_wave_port(sig_p.id, sig_path[-1], "wave_port", 50, 10, 10)
        pyaedt_edb.appedb.core_hfss.create_differential_wave_port(
            sig_p_0.id, sig_path_p_0[-1], sig_n_0.id, sig_path_n_0[-1], "port_0", 8, 8
        )
        pyaedt_edb.appedb.core_hfss.create_differential_wave_port(
            sig_p_1.id, sig_path_p_1[-1], sig_n_1.id, sig_path_n_1[-1], "port_1", 8, 3
        )

        setup = pyaedt_edb.appedb.create_hfss_setup("setup1")

        setup.set_solution_multi_frequencies(("5GHz", "12.5GHz", "20GHz"))

        setup.via_settings.via_num_sides = 12
        setup.curve_approx_settings.arc_angle = "15deg"
        setup.curve_approx_settings.max_arc_points = 16

        sweep = setup.add_frequency_sweep("sweep1")
        sweep.set_frequencies_linear_scale("5GHz", stop="20GHz", step="0.5GHz")
        project_name = "_".join([self.name, self.sig_layers[0], self.sig_layers[-1]])

        pyaedt_edb._save_edb_and_close(project_name)
        if save_as_aedt:
            pyaedt_edb._save_as_aedt(project_name)


if __name__ == '__main__':
    DiffPairType1(work_dir=r"C:\ansysdev\_aedt_workspace\pyaedt_pcb_design").create()
