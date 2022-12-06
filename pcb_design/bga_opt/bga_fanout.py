from pcb_design.base_3d import Bench3DL


class BgaFanoutType1(Bench3DL):

    def __init__(self, name="bga_fanout", sig_layer="TOP", layer_count=2, work_dir=None):
        Bench3DL.__init__(self, work_dir)
        self.name = name
        self.sig_layer = sig_layer
        self.layer_count = layer_count

    def run(self):
        self.appedb.add_design_variable("$sig_width", "0.075mm")
        self.appedb.add_design_variable("$sig_clr", "0.3mm")
        self.appedb.add_design_variable("$via_distance", "0.8mm")



        # Place pin/via
        data = {
            0: [0, 0, 0],
            1: [0, 1, 0]
        }
        self.gnd_planes = self.init_design(self.layer_count)
        for x, d in data.items():
            for y, value in enumerate(d):
                x_loc = "$drill_offset_x+{}*$via_distance".format(x)
                y_loc = "$drill_offset_y+{}*$via_distance".format(y)
                if value == 1:
                    net_name = "sig"
                    sig_path = [(x_loc, y_loc), (self.x_limit_p, y_loc)]
                    sig = self.appedb.core_primitives.create_trace(
                        sig_path,
                        layer_name=self.sig_layer,
                        width="$sig_width",
                        net_name="SIG",
                        end_cap_style="Flat"
                    )
                    sig_void = self.appedb.core_primitives.create_trace(
                        sig_path,
                        layer_name=self.sig_layer,
                        width="$sig_width+$sig_clr*2",
                        net_name="GND",
                        start_cap_style="Flat",
                        end_cap_style="Flat"
                    )
                else:
                    net_name = "gnd"
                pos = [x_loc, y_loc]
                self.appedb.core_padstack.place_padstack(pos, "via_200", net_name=net_name, is_pin=True)

        self.appedb.core_primitives.add_void(self.gnd_planes[self.sig_layer], sig_void.primitive_object)
        self.appedb.core_hfss.create_wave_port(sig.id, sig_path[-1], "wave_port", 50, 10, 10)

        self.save_edb_and_close(self.name)


if __name__ == '__main__':
    BgaFanoutType1(layer_count=2,
                   work_dir=r"C:\ansysdev\_aedt_workspace\pyaedt_pcb_design").run()
