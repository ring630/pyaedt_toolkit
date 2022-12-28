import os
from pyaedt import Edb


class Bench3DL:

    def __init__(self, work_dir):
        if work_dir:
            os.chdir(work_dir)

        self.x_limit_p = "2mm"
        self.x_limit_n = "-2mm"
        self.y_limit_p = "3mm"
        self.y_limit_n = "-1mm"

        self.appedb = Edb(edbversion="2022.2")

    def add_default_variables(self):
        variables = {
            "$antipad_size": "1mm",
            "$drill_offset_x": "0mm",
            "$drill_offset_y": "0mm",
            "$etching_tol": "0mm"
        }
        for var, val in variables.items():
            self.appedb.add_design_variable(var, val)

    def add_default_padstacks(self):
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

    def create_board(self, layer_count=2, dielectric_thickness="100um"):
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

    def save_edb_and_close(self, aedb_name):
        self.appedb.save_edb_as(aedb_name)
        self.appedb.close_edb()