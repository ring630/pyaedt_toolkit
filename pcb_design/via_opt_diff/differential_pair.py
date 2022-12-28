from pcb_design.base_3d import Bench3DL


class DiffPairType1(Bench3DL):

    def __init__(
            self,
            name="diff_pair_type_1",
            sig_layers=("TOP", "L4"),
            layer_count=8,
            dielectric_thickness="150um",
            work_dir=None):
        Bench3DL.__init__(self, work_dir)
        self.name = name
        self.sig_layers = sig_layers
        self.layer_count = layer_count
        self.dielectric_thickness = dielectric_thickness
        self.gnd_planes = None

    def run(self):
        self.appedb.add_design_variable("$sig_width_0", "0.1mm")
        self.appedb.add_design_variable("$sig_gap_0", "0.15mm")
        self.appedb.add_design_variable("$sig_width_1", "0.075mm")
        self.appedb.add_design_variable("$sig_gap_1", "0.1mm")
        self.appedb.add_design_variable("$via_distance", "0.8mm")

        # Place pin/via
        data = {
            0: ["GND", "SIG_P", "SIG_N", "GND"]
        }
        self.gnd_planes = self.create_board(self.layer_count, self.dielectric_thickness)
        self.add_default_variables()
        self.add_default_padstacks()

        self.gnd_planes[self.sig_layers[0]].delete()
        self.gnd_planes[self.sig_layers[1]].delete()
        for name, val in self.appedb.stackup.layers.items():
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
                    sig_path_p_0 = [(x_loc, y_loc), (x_loc_2, y_loc_2), (self.x_limit_n, y_loc_2)]
                    sig_p_0 = self.appedb.core_primitives.create_trace(
                        sig_path_p_0,
                        layer_name=self.sig_layers[0],
                        width="$sig_width_0",
                        net_name=net_name,
                        end_cap_style="Flat"
                    )
                    x_loc_2 = "{}+{}".format(x_loc, "($via_distance-$sig_gap_1-$sig_width_1)/2")
                    y_loc_2 = "{}+{}".format(y_loc, "($via_distance-$sig_gap_1-$sig_width_1)/2")
                    sig_path_p_1 = [(x_loc, y_loc), (x_loc_2, y_loc_2), (self.x_limit_p, y_loc_2)]
                    sig_p_1 = self.appedb.core_primitives.create_trace(
                        sig_path_p_1,
                        layer_name=self.sig_layers[1],
                        width="$sig_width_1",
                        net_name=net_name,
                        end_cap_style="Flat"
                    )
                elif net_name.endswith("_N"):
                    x_loc_2 = "{}-{}".format(x_loc, "($via_distance-$sig_gap_0-$sig_width_0)/2")
                    y_loc_2 = "{}-{}".format(y_loc, "($via_distance-$sig_gap_0-$sig_width_0)/2")
                    sig_path_n_0 = [(x_loc, y_loc), (x_loc_2, y_loc_2), (self.x_limit_n, y_loc_2)]
                    sig_n_0 = self.appedb.core_primitives.create_trace(
                        sig_path_n_0,
                        layer_name=self.sig_layers[0],
                        width="$sig_width_0",
                        net_name=net_name,
                        end_cap_style="Flat"
                    )
                    x_loc_2 = "{}+{}".format(x_loc, "($via_distance-$sig_gap_1-$sig_width_1)/2")
                    y_loc_2 = "{}-{}".format(y_loc, "($via_distance-$sig_gap_1-$sig_width_1)/2")
                    sig_path_n_1 = [(x_loc, y_loc), (x_loc_2, y_loc_2), (self.x_limit_p, y_loc_2)]
                    sig_n_1 = self.appedb.core_primitives.create_trace(
                        sig_path_n_1,
                        layer_name=self.sig_layers[1],
                        width="$sig_width_1",
                        net_name=net_name,
                        end_cap_style="Flat"
                    )

                pos = [via_x_loc, via_y_loc]
                via = self.appedb.core_padstack.place_padstack(pos, "via_200", net_name=net_name)
                if not net_name == "GND":
                    layer = self.sig_layers[-1]
                    via.set_backdrill_bottom(layer, 0.5e-3)

        # self.appedb.core_hfss.create_wave_port(sig_p.id, sig_path[-1], "wave_port", 50, 10, 10)
        self.appedb.core_hfss.create_differential_wave_port(
            sig_p_0.id, sig_path_p_0[-1], sig_n_0.id, sig_path_n_0[-1], "port_0", 8, 8
        )
        self.appedb.core_hfss.create_differential_wave_port(
            sig_p_1.id, sig_path_p_1[-1], sig_n_1.id, sig_path_n_1[-1], "port_1", 8, 3
        )

        setup = self.appedb.create_hfss_setup("setup1")

        setup.set_solution_multi_frequencies(("5GHz", "12.5GHz", "20GHz"))

        setup.via_settings.via_num_sides = 12
        setup.curve_approx_settings.arc_angle = "15deg"
        setup.curve_approx_settings.max_arc_points = 16

        sweep = setup.add_frequency_sweep("sweep1")
        sweep.set_frequencies_linear_scale("5GHz", stop="20GHz", step="0.5GHz")
        project_name = "_".join([self.name, self.sig_layers[0], self.sig_layers[-1]])
        self.save_edb_and_close(project_name)


if __name__ == '__main__':
    DiffPairType1(
        sig_layers=("TOP", "L6"),
        layer_count=8,
        dielectric_thickness="200um",
        work_dir=r"C:\ansysdev\_aedt_workspace\pyaedt_pcb_design").run()
