import os

from pyaedt import Q2d


class MyVars:

    def __init__(self):
        self._etching = ["etching", 2]
        #self._x_limit_l = ["x_limit_l", "-1mm"]
        #self._x_limit_r = ["x_limit_r", "1mm"]
        self._cond_h = ["cond_h", "0.017mm"]
        self._diel_1_h = ["diel_1_h", "0.15mm"]
        self._diel_2_h = ["diel_2_h", "0.15mm"]
        self._sm_h = ["sm_h", "0.02mm"]

        self._sig_w = ["sig_w", "0.075mm"]
        self._sig_gap = ["sig_gap", "0.1mm"]
        self._clearance = ["clearance", "0.1mm"]

        self._co_gnd_w = ["co_gnd_w", "0.5mm"]

        self._delta_etching = ["delta_etching", "0mm"]

    @property
    def etching(self):
        return self._etching[0]

    """@property
    def x_limit_l(self):
        return self._x_limit_l[0]

    @property
    def x_limit_r(self):
        return self._x_limit_r[0]"""

    @property
    def cond_h(self):
        return self._cond_h[0]

    @property
    def diel_1_h(self):
        return self._diel_1_h[0]

    @property
    def diel_2_h(self):
        return self._diel_2_h[0]

    @property
    def sig_w(self):
        return "({}-{}*2)".format(self._sig_w[0], self._delta_etching[0])

    @property
    def sig_gap(self):
        return "({}+{}*2)".format(self._sig_gap[0], self._delta_etching[0])

    @property
    def clearance(self):
        return "({}+{}*2)".format(self._clearance[0], self._delta_etching[0])

    @property
    def co_gnd_w(self):
        return self._co_gnd_w[0]

    @property
    def sm_h(self):
        return self._sm_h[0]


class TransLine2D:
    def __init__(self):

        non_graphical = os.getenv("PYAEDT_NON_GRAPHICAL", "False").lower() in ("true", "1", "t")
        self.q2d = Q2d(
            specified_version="2022.2", non_graphical=non_graphical, new_desktop_session=True)

        self.q2d["$dk"] = 4
        self.q2d["$df"] = 0.005
        self.q2d["$ra"] = "0.2um"
        self.q2d["$sr"] = "5"

        my_mat = self.q2d.materials.add_material("my_fr4")
        my_mat.permittivity = "$dk"
        my_mat.dielectric_loss_tangent = "$df"
        my_mat.material_appearance = [0, 128, 0]

    def add_setup(self, q2d):
        setup = q2d.create_setup(setupname="new_setup")
        sweep = setup.add_sweep(sweepname="sweep1")
        sweep.props["RangeType"] = "LinearStep"
        sweep.props["RangeStart"] = "1GHz"
        sweep.props["RangeStep"] = "0.5GHz"
        sweep.props["RangeEnd"] = "10GHz"
        sweep.props["SaveFields"] = False
        sweep.props["SaveRadFields"] = False
        sweep.update()
    def save_and_close(self, name, work_dir):
        self.q2d.save_project(os.path.join(work_dir, name))
        self.q2d.close_desktop()

    def differential_stripline(self):
        self.q2d.insert_design("differntial_stripline")
        design_vars = MyVars()
        for name, val in design_vars.__dict__.items():
            self.q2d[val[0]] = val[1]

        delta_w_half = "({0}/{1})".format(design_vars.cond_h, design_vars.etching)
        sig_top_w = "({1}-{0}*2)".format(delta_w_half, design_vars.sig_w)
        co_gnd_top_w = "({1}-{0})".format(delta_w_half, design_vars.co_gnd_w)

        ###############################################################################
        # Create primitives
        # ~~~~~~~~~~~~~~~~~
        # Create primitives and define the layer heights.

        layer_1_lh = 0
        layer_1_uh = design_vars.cond_h

        layer_2_lh = layer_1_uh + "+" + design_vars.diel_1_h
        layer_2_uh = layer_2_lh + "+" + design_vars.cond_h

        layer_3_lh = layer_2_uh + "+" + design_vars.diel_2_h
        layer_3_uh = layer_3_lh + "+" + design_vars.cond_h

        model_w = "{}*2+{}*2+{}*2+{}".format(design_vars.co_gnd_w, design_vars.clearance, design_vars.sig_w, design_vars.sig_gap)

        ###############################################################################
        # Create positive signal
        # ~~~~~~~~~~~~~~~~~~~~~~
        # Create a positive signal.

        base_line_obj = self.q2d.modeler.create_polyline([[0, layer_2_lh, 0], [design_vars.sig_w, layer_2_lh, 0]],
                                                         name="signal_p")
        top_line_obj = self.q2d.modeler.create_polyline([[0, layer_2_uh, 0], [sig_top_w, layer_2_uh, 0]])
        self.q2d.modeler.move([top_line_obj], [delta_w_half, 0, 0])
        self.q2d.modeler.connect([base_line_obj, top_line_obj])
        self.q2d.modeler.move([base_line_obj], ["{}+{}".format(design_vars.co_gnd_w, design_vars.clearance), 0, 0])

        # Create negative signal
        # ~~~~~~~~~~~~~~~~~~~~~~
        # Create a negative signal.

        base_line_obj = self.q2d.modeler.create_polyline([[0, layer_2_lh, 0], [design_vars.sig_w, layer_2_lh, 0]],
                                                         name="signal_n")
        top_line_obj = self.q2d.modeler.create_polyline([[0, layer_2_uh, 0], [sig_top_w, layer_2_uh, 0]])
        self.q2d.modeler.move([top_line_obj], [delta_w_half, 0, 0])
        self.q2d.modeler.connect([base_line_obj, top_line_obj])
        self.q2d.modeler.move([base_line_obj],
                              ["{}+{}+{}+{}".format(design_vars.co_gnd_w, design_vars.clearance, design_vars.sig_w, design_vars.sig_gap), 0, 0])

        ###############################################################################
        # Create coplanar ground
        # ~~~~~~~~~~~~~~~~~~~~~~
        # Create a coplanar ground.

        base_line_obj = self.q2d.modeler.create_polyline([[0, layer_2_lh, 0], [design_vars.co_gnd_w, layer_2_lh, 0]],
                                                         name="co_gnd_left")
        top_line_obj = self.q2d.modeler.create_polyline([[0, layer_2_uh, 0], [co_gnd_top_w, layer_2_uh, 0]])
        # self.q2d.modeler.move([top_line_obj], [delta_w_half, 0, 0])
        self.q2d.modeler.connect([base_line_obj, top_line_obj])

        base_line_obj = self.q2d.modeler.create_polyline([[0, layer_2_lh, 0], [design_vars.co_gnd_w, layer_2_lh, 0]],
                                                         name="co_gnd_right")
        top_line_obj = self.q2d.modeler.create_polyline([[0, layer_2_uh, 0], [co_gnd_top_w, layer_2_uh, 0]])
        self.q2d.modeler.move([top_line_obj], [delta_w_half, 0, 0])
        self.q2d.modeler.connect([base_line_obj, top_line_obj])
        self.q2d.modeler.move([base_line_obj],
                              ["{}+{}*2+{}*2+{}".format(design_vars.co_gnd_w, design_vars.clearance, design_vars.sig_w, design_vars.sig_gap), 0,
                               0])

        ###############################################################################
        # Create reference ground plane
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Create a reference ground plane.

        self.q2d.modeler.create_rectangle(position=[0, layer_1_lh, 0], dimension_list=[model_w, design_vars.cond_h],
                                          name="ref_gnd_l")
        self.q2d.modeler.create_rectangle(position=[0, layer_3_lh, 0], dimension_list=[model_w, design_vars.cond_h],
                                          name="ref_gnd_u")

        ###############################################################################
        # Create dielectric
        # ~~~~~~~~~~~~~~~~~
        # Create a dielectric.

        self.q2d.modeler.create_rectangle(
            position=[0, layer_1_uh, 0], dimension_list=[model_w, design_vars.diel_1_h], name="Core", matname="my_fr4"
        )
        self.q2d.modeler.create_rectangle(
            position=[0, layer_2_uh, 0], dimension_list=[model_w, design_vars.diel_2_h], name="Prepreg", matname="my_fr4"
        )
        self.q2d.modeler.create_rectangle(
            position=[0, layer_2_lh, 0], dimension_list=[model_w, design_vars.cond_h], name="Filling", matname="my_fr4"
        )

        ###############################################################################
        # Assign conductors
        # ~~~~~~~~~~~~~~~~~
        # Assign conductors to the signal.

        obj = self.q2d.modeler.get_object_from_name("signal_p")
        self.q2d.assign_single_conductor(
            name=obj.name, target_objects=[obj], conductor_type="SignalLine", solve_option="SolveOnBoundary", unit="mm"
        )

        obj = self.q2d.modeler.get_object_from_name("signal_n")
        self.q2d.assign_single_conductor(
            name=obj.name, target_objects=[obj], conductor_type="SignalLine", solve_option="SolveOnBoundary", unit="mm"
        )

        ###############################################################################
        # Reference ground
        # ~~~~~~~~~~~~~~~~
        # Reference the ground

        obj = [self.q2d.modeler.get_object_from_name(i) for i in
               ["ref_gnd_u", "ref_gnd_l", "co_gnd_left", "co_gnd_right"]]
        self.q2d.assign_single_conductor(
            name="gnd", target_objects=obj, conductor_type="ReferenceGround", solve_option="SolveOnBoundary", unit="mm"
        )

        ###############################################################################
        # Assign Huray model on signals
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Assign the Huray model on the signals.

        obj = self.q2d.modeler.get_object_from_name("signal_p")
        self.q2d.assign_huray_finitecond_to_edges(obj.edges, radius="$ra", ratio="$sr", name="b_" + obj.name)

        obj = self.q2d.modeler.get_object_from_name("signal_n")
        self.q2d.assign_huray_finitecond_to_edges(obj.edges, radius="$ra", ratio="$sr", name="b_" + obj.name)

        ###############################################################################
        # Define differnetial pair
        # ~~~~~~~~~~~~~~~~~~~~~~~~
        # Define the differential pair.

        matrix = self.q2d.insert_reduced_matrix(self.q2d.MATRIXOPERATIONS.DiffPair, ["signal_p", "signal_n"],
                                                rm_name="diff_pair")

        ###############################################################################
        # Create setup, analyze, and plot
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Create a setup, analyze, and plot solution data.

        self.add_setup(self.q2d)

    def differential_microstrip(self):
        self.q2d.insert_design("differential_microstrip")

        design_vars = MyVars()
        design_vars._cond_h[1] = "0.05mm"
        design_vars._sig_w[1] = "0.14mm"
        design_vars._sig_gap[1] = "0.15mm"
        design_vars._clearance[1] = "0.5mm"

        for name, val in design_vars.__dict__.items():
            self.q2d[val[0]] = val[1]

        delta_w_half = "({0}/{1})".format(design_vars.cond_h, design_vars.etching)
        sig_top_w = "({1}-{0}*2)".format(delta_w_half, design_vars.sig_w)
        co_gnd_top_w = "({1}-{0})".format(delta_w_half, design_vars.co_gnd_w)

        ###############################################################################
        # Create primitives
        # ~~~~~~~~~~~~~~~~~
        # Create primitives and define the layer heights.

        layer_1_lh = 0
        layer_1_uh = design_vars.cond_h

        layer_2_lh = layer_1_uh + "+" + design_vars.diel_1_h
        layer_2_uh = layer_2_lh + "+" + design_vars.cond_h

        layer_air = layer_2_uh + "+" + design_vars.sm_h

        model_w = "{}*2+{}*2+{}*2+{}".format(design_vars.co_gnd_w, design_vars.clearance, design_vars.sig_w, design_vars.sig_gap)

        ###############################################################################
        # Create positive signal
        # ~~~~~~~~~~~~~~~~~~~~~~
        # Create a positive signal.

        base_line_obj = self.q2d.modeler.create_polyline([[0, layer_2_lh, 0], [design_vars.sig_w, layer_2_lh, 0]],
                                                         name="signal_p")
        top_line_obj = self.q2d.modeler.create_polyline([[0, layer_2_uh, 0], [sig_top_w, layer_2_uh, 0]])
        self.q2d.modeler.move([top_line_obj], [delta_w_half, 0, 0])
        self.q2d.modeler.connect([base_line_obj, top_line_obj])
        self.q2d.modeler.move([base_line_obj], ["{}+{}".format(design_vars.co_gnd_w, design_vars.clearance), 0, 0])

        # Create negative signal
        # ~~~~~~~~~~~~~~~~~~~~~~
        # Create a negative signal.

        base_line_obj = self.q2d.modeler.create_polyline([[0, layer_2_lh, 0], [design_vars.sig_w, layer_2_lh, 0]],
                                                         name="signal_n")
        top_line_obj = self.q2d.modeler.create_polyline([[0, layer_2_uh, 0], [sig_top_w, layer_2_uh, 0]])
        self.q2d.modeler.move([top_line_obj], [delta_w_half, 0, 0])
        self.q2d.modeler.connect([base_line_obj, top_line_obj])
        self.q2d.modeler.move([base_line_obj],
                              ["{}+{}+{}+{}".format(design_vars.co_gnd_w, design_vars.clearance, design_vars.sig_w, design_vars.sig_gap), 0, 0])

        ###############################################################################
        # Create coplanar ground
        # ~~~~~~~~~~~~~~~~~~~~~~
        # Create a coplanar ground.

        base_line_obj = self.q2d.modeler.create_polyline([[0, layer_2_lh, 0], [design_vars.co_gnd_w, layer_2_lh, 0]],
                                                         name="co_gnd_left")
        top_line_obj = self.q2d.modeler.create_polyline([[0, layer_2_uh, 0], [co_gnd_top_w, layer_2_uh, 0]])
        # self.q2d.modeler.move([top_line_obj], [delta_w_half, 0, 0])
        self.q2d.modeler.connect([base_line_obj, top_line_obj])

        base_line_obj = self.q2d.modeler.create_polyline([[0, layer_2_lh, 0], [design_vars.co_gnd_w, layer_2_lh, 0]],
                                                         name="co_gnd_right")
        top_line_obj = self.q2d.modeler.create_polyline([[0, layer_2_uh, 0], [co_gnd_top_w, layer_2_uh, 0]])
        self.q2d.modeler.move([top_line_obj], [delta_w_half, 0, 0])
        self.q2d.modeler.connect([base_line_obj, top_line_obj])
        self.q2d.modeler.move([base_line_obj],
                              ["{}+{}*2+{}*2+{}".format(design_vars.co_gnd_w, design_vars.clearance, design_vars.sig_w, design_vars.sig_gap), 0,
                               0])

        ###############################################################################
        # Create reference ground plane
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Create a reference ground plane.

        self.q2d.modeler.create_rectangle(position=[0, layer_1_lh, 0], dimension_list=[model_w, design_vars.cond_h],
                                          name="ref_gnd_l")

        ###############################################################################
        # Create dielectric
        # ~~~~~~~~~~~~~~~~~
        # Create a dielectric.

        self.q2d.modeler.create_rectangle(
            position=[0, layer_1_uh, 0], dimension_list=[model_w, design_vars.diel_1_h], name="Core", matname="my_fr4"
        )
        self.q2d.modeler.create_rectangle(
            position=[0, layer_2_uh, 0], dimension_list=[model_w, design_vars.sm_h], name="Sm", matname="Soldermask"
        )
        self.q2d.modeler.create_rectangle(
            position=[0, layer_air, 0], dimension_list=[model_w, "1mm"], name="air", matname="Air"
        )
        self.q2d.modeler.create_rectangle(
            position=[0, layer_2_lh, 0], dimension_list=[model_w, design_vars.cond_h], name="Filling", matname="Soldermask"
        )

        ###############################################################################
        # Assign conductors
        # ~~~~~~~~~~~~~~~~~
        # Assign conductors to the signal.

        obj = self.q2d.modeler.get_object_from_name("signal_p")
        self.q2d.assign_single_conductor(
            name=obj.name, target_objects=[obj], conductor_type="SignalLine", solve_option="SolveOnBoundary", unit="mm"
        )

        obj = self.q2d.modeler.get_object_from_name("signal_n")
        self.q2d.assign_single_conductor(
            name=obj.name, target_objects=[obj], conductor_type="SignalLine", solve_option="SolveOnBoundary", unit="mm"
        )

        ###############################################################################
        # Reference ground
        # ~~~~~~~~~~~~~~~~
        # Reference the ground

        obj = [self.q2d.modeler.get_object_from_name(i) for i in
               ["ref_gnd_l", "co_gnd_left", "co_gnd_right"]]
        self.q2d.assign_single_conductor(
            name="gnd", target_objects=obj, conductor_type="ReferenceGround", solve_option="SolveOnBoundary", unit="mm"
        )

        ###############################################################################
        # Assign Huray model on signals
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Assign the Huray model on the signals.

        obj = self.q2d.modeler.get_object_from_name("signal_p")
        self.q2d.assign_huray_finitecond_to_edges(obj.edges, radius="$ra", ratio="$sr", name="b_" + obj.name)

        obj = self.q2d.modeler.get_object_from_name("signal_n")
        self.q2d.assign_huray_finitecond_to_edges(obj.edges, radius="$ra", ratio="$sr", name="b_" + obj.name)

        ###############################################################################
        # Define differnetial pair
        # ~~~~~~~~~~~~~~~~~~~~~~~~
        # Define the differential pair.

        matrix = self.q2d.insert_reduced_matrix(self.q2d.MATRIXOPERATIONS.DiffPair, ["signal_p", "signal_n"],
                                                rm_name="diff_pair")

        ###############################################################################
        # Create setup, analyze, and plot
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Create a setup, analyze, and plot solution data.

        self.add_setup(self.q2d)

    def coplanar_waveguide_with_ground(self, soldermask=False):
        self.q2d.insert_design("coplanar_waveguide_with_ground")
        design_vars = MyVars()
        design_vars._cond_h[1] = "0.05mm"
        design_vars._sig_w[1] = "0.14mm"
        design_vars._clearance[1] = "0.5mm"

        for name, val in design_vars.__dict__.items():
            if isinstance(val, list):
                self.q2d[val[0]] = val[1]

        delta_w_half = "({0}/{1})".format(design_vars.cond_h, design_vars.etching)
        sig_top_w = "({1}-{0}*2)".format(delta_w_half, design_vars.sig_w)
        co_gnd_top_w = "({1}-{0})".format(delta_w_half, design_vars.co_gnd_w)

        ###############################################################################
        # Create primitives
        # ~~~~~~~~~~~~~~~~~
        # Create primitives and define the layer heights.

        layer_1_lh = 0
        layer_1_uh = design_vars.cond_h

        layer_2_lh = layer_1_uh + "+" + design_vars.diel_1_h
        layer_2_uh = layer_2_lh + "+" + design_vars.cond_h

        layer_air = layer_2_uh + "+" + design_vars.sm_h

        model_w = "{}*2+{}*2+{}".format(design_vars.co_gnd_w, design_vars.clearance, design_vars.sig_w)

        ###############################################################################
        # Create positive signal
        # ~~~~~~~~~~~~~~~~~~~~~~
        # Create a positive signal.

        base_line_obj = self.q2d.modeler.create_polyline([[0, layer_2_lh, 0], [design_vars.sig_w, layer_2_lh, 0]],
                                                         name="signal_p")
        top_line_obj = self.q2d.modeler.create_polyline([[0, layer_2_uh, 0], [sig_top_w, layer_2_uh, 0]])
        self.q2d.modeler.move([top_line_obj], [delta_w_half, 0, 0])
        self.q2d.modeler.connect([base_line_obj, top_line_obj])
        self.q2d.modeler.move([base_line_obj], ["{}+{}".format(design_vars.co_gnd_w, design_vars.clearance), 0, 0])

        ###############################################################################
        # Create coplanar ground
        # ~~~~~~~~~~~~~~~~~~~~~~
        # Create a coplanar ground.

        base_line_obj = self.q2d.modeler.create_polyline([[0, layer_2_lh, 0], [design_vars.co_gnd_w, layer_2_lh, 0]],
                                                         name="co_gnd_left")
        top_line_obj = self.q2d.modeler.create_polyline([[0, layer_2_uh, 0], [co_gnd_top_w, layer_2_uh, 0]])
        # self.q2d.modeler.move([top_line_obj], [delta_w_half, 0, 0])
        self.q2d.modeler.connect([base_line_obj, top_line_obj])

        base_line_obj = self.q2d.modeler.create_polyline([[0, layer_2_lh, 0], [design_vars.co_gnd_w, layer_2_lh, 0]],
                                                         name="co_gnd_right")
        top_line_obj = self.q2d.modeler.create_polyline([[0, layer_2_uh, 0], [co_gnd_top_w, layer_2_uh, 0]])
        self.q2d.modeler.move([top_line_obj], [delta_w_half, 0, 0])
        self.q2d.modeler.connect([base_line_obj, top_line_obj])
        self.q2d.modeler.move([base_line_obj],
                              ["{}+{}*2+{}".format(design_vars.co_gnd_w, design_vars.clearance, design_vars.sig_w), 0,
                               0])

        ###############################################################################
        # Create reference ground plane
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Create a reference ground plane.

        self.q2d.modeler.create_rectangle(position=[0, layer_1_lh, 0], dimension_list=[model_w, design_vars.cond_h],
                                          name="ref_gnd_l")

        ###############################################################################
        # Create dielectric
        # ~~~~~~~~~~~~~~~~~
        # Create a dielectric.

        self.q2d.modeler.create_rectangle(
            position=[0, layer_1_uh, 0], dimension_list=[model_w, design_vars.diel_1_h], name="Core", matname="my_fr4"
        )
        self.q2d.modeler.create_rectangle(
            position=[0, layer_air, 0], dimension_list=[model_w, "1mm"], name="air", matname="Air"
        )
        if soldermask:
            self.q2d.modeler.create_rectangle(
                position=[0, layer_2_uh, 0], dimension_list=[model_w, design_vars.sm_h], name="Sm", matname="Soldermask"
            )
            self.q2d.modeler.create_rectangle(
                position=[0, layer_2_lh, 0], dimension_list=[model_w, design_vars.cond_h], name="Filling", matname="Soldermask"
            )

        ###############################################################################
        # Assign conductors
        # ~~~~~~~~~~~~~~~~~
        # Assign conductors to the signal.

        obj = self.q2d.modeler.get_object_from_name("signal_p")
        self.q2d.assign_single_conductor(
            name=obj.name, target_objects=[obj], conductor_type="SignalLine", solve_option="SolveOnBoundary", unit="mm"
        )

        ###############################################################################
        # Reference ground
        # ~~~~~~~~~~~~~~~~
        # Reference the ground

        obj = [self.q2d.modeler.get_object_from_name(i) for i in
               ["ref_gnd_l", "co_gnd_left", "co_gnd_right"]]
        self.q2d.assign_single_conductor(
            name="gnd", target_objects=obj, conductor_type="ReferenceGround", solve_option="SolveOnBoundary", unit="mm"
        )

        ###############################################################################
        # Assign Huray model on signals
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Assign the Huray model on the signals.

        obj = self.q2d.modeler.get_object_from_name("signal_p")
        self.q2d.assign_huray_finitecond_to_edges(obj.edges, radius="$ra", ratio="$sr", name="b_" + obj.name)

        ###############################################################################
        # Create setup, analyze, and plot
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Create a setup, analyze, and plot solution data.

        self.add_setup(self.q2d)

    def coplanar_waveguide(self, soldermask=False):
        self.q2d.insert_design("coplanar_waveguide")
        design_vars = MyVars()
        design_vars._cond_h[1] = "0.05mm"
        design_vars._diel_1_h[1] = "0.5mm"
        design_vars._sig_w[1] = "1.5mm"
        design_vars._clearance[1] = "0.15mm"
        design_vars._co_gnd_w[1] = "2mm"

        for name, val in design_vars.__dict__.items():
            if isinstance(val, list):
                self.q2d[val[0]] = val[1]

        delta_w_half = "({0}/{1})".format(design_vars.cond_h, design_vars.etching)
        sig_top_w = "({1}-{0}*2)".format(delta_w_half, design_vars.sig_w)
        co_gnd_top_w = "({1}-{0})".format(delta_w_half, design_vars.co_gnd_w)

        ###############################################################################
        # Create primitives
        # ~~~~~~~~~~~~~~~~~
        # Create primitives and define the layer heights.

        layer_1_lh = 0
        layer_1_uh = design_vars.cond_h

        layer_2_lh = layer_1_uh + "+" + design_vars.diel_1_h
        layer_2_uh = layer_2_lh + "+" + design_vars.cond_h

        layer_air = layer_2_uh + "+" + design_vars.sm_h

        model_w = "{}*2+{}*2+{}".format(design_vars.co_gnd_w, design_vars.clearance, design_vars.sig_w)

        ###############################################################################
        # Create positive signal
        # ~~~~~~~~~~~~~~~~~~~~~~
        # Create a positive signal.

        base_line_obj = self.q2d.modeler.create_polyline([[0, layer_2_lh, 0], [design_vars.sig_w, layer_2_lh, 0]],
                                                         name="signal_p")
        top_line_obj = self.q2d.modeler.create_polyline([[0, layer_2_uh, 0], [sig_top_w, layer_2_uh, 0]])
        self.q2d.modeler.move([top_line_obj], [delta_w_half, 0, 0])
        self.q2d.modeler.connect([base_line_obj, top_line_obj])
        self.q2d.modeler.move([base_line_obj], ["{}+{}".format(design_vars.co_gnd_w, design_vars.clearance), 0, 0])

        ###############################################################################
        # Create coplanar ground
        # ~~~~~~~~~~~~~~~~~~~~~~
        # Create a coplanar ground.

        base_line_obj = self.q2d.modeler.create_polyline([[0, layer_2_lh, 0], [design_vars.co_gnd_w, layer_2_lh, 0]],
                                                         name="co_gnd_left")
        top_line_obj = self.q2d.modeler.create_polyline([[0, layer_2_uh, 0], [co_gnd_top_w, layer_2_uh, 0]])
        # self.q2d.modeler.move([top_line_obj], [delta_w_half, 0, 0])
        self.q2d.modeler.connect([base_line_obj, top_line_obj])

        base_line_obj = self.q2d.modeler.create_polyline([[0, layer_2_lh, 0], [design_vars.co_gnd_w, layer_2_lh, 0]],
                                                         name="co_gnd_right")
        top_line_obj = self.q2d.modeler.create_polyline([[0, layer_2_uh, 0], [co_gnd_top_w, layer_2_uh, 0]])
        self.q2d.modeler.move([top_line_obj], [delta_w_half, 0, 0])
        self.q2d.modeler.connect([base_line_obj, top_line_obj])
        self.q2d.modeler.move([base_line_obj],
                              ["{}+{}*2+{}".format(design_vars.co_gnd_w, design_vars.clearance, design_vars.sig_w), 0,
                               0])

        ###############################################################################
        # Create dielectric
        # ~~~~~~~~~~~~~~~~~
        # Create a dielectric.

        self.q2d.modeler.create_rectangle(
            position=[0, layer_1_uh, 0], dimension_list=[model_w, design_vars.diel_1_h], name="Core", matname="my_fr4"
        )

        self.q2d.modeler.create_rectangle(
            position=[0, "-1mm", 0], dimension_list=[model_w, "4mm"], name="air", matname="Air"
        )

        if soldermask:
            self.q2d.modeler.create_rectangle(
                position=[0, layer_2_uh, 0], dimension_list=[model_w, design_vars.sm_h], name="Sm", matname="Soldermask"
            )
            self.q2d.modeler.create_rectangle(
                position=[0, layer_2_lh, 0], dimension_list=[model_w, design_vars.cond_h], name="Filling", matname="Soldermask"
            )

        ###############################################################################
        # Assign conductors
        # ~~~~~~~~~~~~~~~~~
        # Assign conductors to the signal.

        obj = self.q2d.modeler.get_object_from_name("signal_p")
        self.q2d.assign_single_conductor(
            name=obj.name, target_objects=[obj], conductor_type="SignalLine", solve_option="SolveOnBoundary", unit="mm"
        )

        ###############################################################################
        # Reference ground
        # ~~~~~~~~~~~~~~~~
        # Reference the ground

        obj = [self.q2d.modeler.get_object_from_name(i) for i in
               ["co_gnd_left", "co_gnd_right"]]
        self.q2d.assign_single_conductor(
            name="gnd", target_objects=obj, conductor_type="ReferenceGround", solve_option="SolveOnBoundary", unit="mm"
        )

        ###############################################################################
        # Assign Huray model on signals
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Assign the Huray model on the signals.

        obj = self.q2d.modeler.get_object_from_name("signal_p")
        self.q2d.assign_huray_finitecond_to_edges(obj.edges, radius="$ra", ratio="$sr", name="b_" + obj.name)

        ###############################################################################
        # Create setup, analyze, and plot
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Create a setup, analyze, and plot solution data.

        self.add_setup(self.q2d)


if __name__ == '__main__':
    """
    trans = TransLine2D()
    trans.create_differential_stripline("differential_stripline.aedt",
                                        r"C:\ansysdev\_aedt_workspace\pyaedt_pcb_design\q2d_transmissionline")
    """
    trans = TransLine2D()
    trans.differential_microstrip()
    trans.differential_stripline()
    trans.coplanar_waveguide_with_ground()
    trans.coplanar_waveguide()
    trans.save_and_close("transmissionline.aedt",
                         r"C:\ansysdev\_aedt_workspace\pyaedt_pcb_design\q2d_transmissionline")
