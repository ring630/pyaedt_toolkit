from pcb_design.base_3d import Bench3DL


class DiffPairType1(Bench3DL):

    def __init__(self, name="diff_pair_type_1", sig_layers=("TOP", "L4"), layer_count=8, work_dir=None):
        Bench3DL.__init__(self, work_dir)
        self.name = name
        self.sig_layers = sig_layers
        self.layer_count = layer_count
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
        self.gnd_planes = self.init_design(self.layer_count)
        self.gnd_planes[self.sig_layers[0]].delete()
        self.gnd_planes[self.sig_layers[1]].delete()

        for x, d in data.items():
            for y, net_name in enumerate(d):
                via_x_loc = "$drill_offset_x+{}*$via_distance".format(x)
                via_y_loc = "$drill_offset_y+{}*$via_distance".format(y)
                x_loc = "{}*$via_distance".format(x)
                y_loc = "{}*$via_distance".format(y)



                if net_name.endswith("_P"):
                    x_loc_2 = "{}-{}".format(x_loc, "($via_distance-$sig_gap_0-$sig_width_0)/2")
                    y_loc_2 = "{}+{}".format(y_loc, "($via_distance-$sig_gap_0-$sig_width_0)/2")
                    sig_path = [(x_loc, y_loc), (x_loc_2, y_loc_2), (self.x_limit_n, y_loc_2)]
                    sig_p_0 = self.appedb.core_primitives.create_trace(
                        sig_path,
                        layer_name=self.sig_layers[0],
                        width="$sig_width_0",
                        net_name=net_name,
                        end_cap_style="Flat"
                    )
                    x_loc_2 = "{}+{}".format(x_loc, "($via_distance-$sig_gap_1-$sig_width_1)/2")
                    y_loc_2 = "{}+{}".format(y_loc, "($via_distance-$sig_gap_1-$sig_width_1)/2")
                    sig_path = [(x_loc, y_loc), (x_loc_2, y_loc_2), (self.x_limit_p, y_loc_2)]
                    sig_p_1 = self.appedb.core_primitives.create_trace(
                        sig_path,
                        layer_name=self.sig_layers[1],
                        width="$sig_width_1",
                        net_name=net_name,
                        end_cap_style="Flat"
                    )
                elif net_name.endswith("_N"):
                    x_loc_2 = "{}-{}".format(x_loc, "($via_distance-$sig_gap_0-$sig_width_0)/2")
                    y_loc_2 = "{}-{}".format(y_loc, "($via_distance-$sig_gap_0-$sig_width_0)/2")
                    sig_path = [(x_loc, y_loc), (x_loc_2, y_loc_2), (self.x_limit_n, y_loc_2)]
                    sig_n_0 = self.appedb.core_primitives.create_trace(
                        sig_path,
                        layer_name=self.sig_layers[0],
                        width="$sig_width_0",
                        net_name=net_name,
                        end_cap_style="Flat"
                    )
                    x_loc_2 = "{}+{}".format(x_loc, "($via_distance-$sig_gap_1-$sig_width_1)/2")
                    y_loc_2 = "{}-{}".format(y_loc, "($via_distance-$sig_gap_1-$sig_width_1)/2")
                    sig_path = [(x_loc, y_loc), (x_loc_2, y_loc_2), (self.x_limit_p, y_loc_2)]
                    sig_n_1 = self.appedb.core_primitives.create_trace(
                        sig_path,
                        layer_name=self.sig_layers[1],
                        width="$sig_width_1",
                        net_name=net_name,
                        end_cap_style="Flat"
                    )

                pos = [via_x_loc, via_y_loc]
                self.appedb.core_padstack.place_padstack(pos, "via_200", net_name=net_name)

        #self.appedb.core_hfss.create_wave_port(sig_p.id, sig_path[-1], "wave_port", 50, 10, 10)

        #self.appedb.core_nets.plot(None)
        self.save_edb_and_close(self.name)



if __name__ == '__main__':
    DiffPairType1(layer_count=8,
                   work_dir=r"C:\ansysdev\_aedt_workspace\pyaedt_pcb_design").run()
