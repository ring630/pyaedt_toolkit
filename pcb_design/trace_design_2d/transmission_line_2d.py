import os

from pyaedt import Q2d


class Var:
    _dk = "$dk", 4
    _df = "$df", 0.005
    _ra = "$ra", "0.2um"
    _sr = "$sr", "5"

    _etching = "etching", 2
    _x_limit_l = "x_limit_l", "-1mm"
    _x_limit_r = "x_limit_r", "1mm"
    _cond_h = "cond_h", "0.017mm"
    _diel_1_h = "diel_1_h", "0.15mm"
    _diel_2_h = "diel_2_h", "0.15mm"
    _sm_h = "sm_h", "0.02mm"

    _sig_w = "sig_w", "0.075mm"
    _sig_gap = "sig_gap", "0.1mm"
    _clearance = "clearance", "0.1mm"

    _co_gnd_w = "co_gnd_w", "0.5mm"

    _delta_etching = "delta_etching", "0"

    @property
    def etching(self):
        return self._etching[0]

    @property
    def x_limit_l(self):
        return self._x_limit_l[0]

    @property
    def x_limit_r(self):
        return self._x_limit_r[0]

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

        for name, val in dict(vars(Var)).items():

            if isinstance(val, tuple):
                self.q2d[val[0]] = val[1]

        my_mat = self.q2d.materials.add_material("my_fr4")
        my_mat.permittivity = "$dk"
        my_mat.dielectric_loss_tangent = "$df"

    def create_differential_stripline(self, name, work_dir):
        delta_w_half = "({0}/{1})".format(Var().cond_h, Var().etching)
        sig_top_w = "({1}-{0}*2)".format(delta_w_half, Var().sig_w)
        co_gnd_top_w = "({1}-{0})".format(delta_w_half, Var().co_gnd_w)

        ###############################################################################
        # Create primitives
        # ~~~~~~~~~~~~~~~~~
        # Create primitives and define the layer heights.

        layer_1_lh = 0
        layer_1_uh = Var().cond_h

        layer_2_lh = layer_1_uh + "+" + Var().diel_1_h
        layer_2_uh = layer_2_lh + "+" + Var().cond_h

        layer_3_lh = layer_2_uh + "+" + Var().diel_2_h
        layer_3_uh = layer_3_lh + "+" + Var().cond_h

        model_w = "{}*2+{}*2+{}*2+{}".format(Var().co_gnd_w, Var().clearance, Var().sig_w, Var().sig_gap)

        ###############################################################################
        # Create positive signal
        # ~~~~~~~~~~~~~~~~~~~~~~
        # Create a positive signal.

        base_line_obj = self.q2d.modeler.create_polyline([[0, layer_2_lh, 0], [Var().sig_w, layer_2_lh, 0]],
                                                         name="signal_p")
        top_line_obj = self.q2d.modeler.create_polyline([[0, layer_2_uh, 0], [sig_top_w, layer_2_uh, 0]])
        self.q2d.modeler.move([top_line_obj], [delta_w_half, 0, 0])
        self.q2d.modeler.connect([base_line_obj, top_line_obj])
        self.q2d.modeler.move([base_line_obj], ["{}+{}".format(Var().co_gnd_w, Var().clearance), 0, 0])

        # Create negative signal
        # ~~~~~~~~~~~~~~~~~~~~~~
        # Create a negative signal.

        base_line_obj = self.q2d.modeler.create_polyline([[0, layer_2_lh, 0], [Var().sig_w, layer_2_lh, 0]],
                                                         name="signal_n")
        top_line_obj = self.q2d.modeler.create_polyline([[0, layer_2_uh, 0], [sig_top_w, layer_2_uh, 0]])
        self.q2d.modeler.move([top_line_obj], [delta_w_half, 0, 0])
        self.q2d.modeler.connect([base_line_obj, top_line_obj])
        self.q2d.modeler.move([base_line_obj],
                              ["{}+{}+{}+{}".format(Var().co_gnd_w, Var().clearance, Var().sig_w, Var().sig_gap), 0, 0])

        ###############################################################################
        # Create coplanar ground
        # ~~~~~~~~~~~~~~~~~~~~~~
        # Create a coplanar ground.

        base_line_obj = self.q2d.modeler.create_polyline([[0, layer_2_lh, 0], [Var().co_gnd_w, layer_2_lh, 0]],
                                                         name="co_gnd_left")
        top_line_obj = self.q2d.modeler.create_polyline([[0, layer_2_uh, 0], [co_gnd_top_w, layer_2_uh, 0]])
        # self.q2d.modeler.move([top_line_obj], [delta_w_half, 0, 0])
        self.q2d.modeler.connect([base_line_obj, top_line_obj])

        base_line_obj = self.q2d.modeler.create_polyline([[0, layer_2_lh, 0], [Var().co_gnd_w, layer_2_lh, 0]],
                                                         name="co_gnd_right")
        top_line_obj = self.q2d.modeler.create_polyline([[0, layer_2_uh, 0], [co_gnd_top_w, layer_2_uh, 0]])
        self.q2d.modeler.move([top_line_obj], [delta_w_half, 0, 0])
        self.q2d.modeler.connect([base_line_obj, top_line_obj])
        self.q2d.modeler.move([base_line_obj],
                              ["{}+{}*2+{}*2+{}".format(Var().co_gnd_w, Var().clearance, Var().sig_w, Var().sig_gap), 0,
                               0])

        ###############################################################################
        # Create reference ground plane
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Create a reference ground plane.

        self.q2d.modeler.create_rectangle(position=[0, layer_1_lh, 0], dimension_list=[model_w, Var().cond_h],
                                          name="ref_gnd_l")
        self.q2d.modeler.create_rectangle(position=[0, layer_3_lh, 0], dimension_list=[model_w, Var().cond_h],
                                          name="ref_gnd_u")

        ###############################################################################
        # Create dielectric
        # ~~~~~~~~~~~~~~~~~
        # Create a dielectric.

        self.q2d.modeler.create_rectangle(
            position=[0, layer_1_uh, 0], dimension_list=[model_w, Var().diel_1_h], name="Core", matname="my_fr4"
        )
        self.q2d.modeler.create_rectangle(
            position=[0, layer_2_uh, 0], dimension_list=[model_w, Var().diel_2_h], name="Prepreg", matname="my_fr4"
        )
        self.q2d.modeler.create_rectangle(
            position=[0, layer_2_lh, 0], dimension_list=[model_w, Var().cond_h], name="Filling", matname="my_fr4"
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

        # Create a setup.
        setup = self.q2d.create_setup(setupname="new_setup")

        # Add a sweep.
        sweep = setup.add_sweep(sweepname="sweep1", sweeptype="Discrete")
        sweep.props["RangeType"] = "LinearStep"
        sweep.props["RangeStart"] = "0.1GHz"
        sweep.props["RangeStep"] = "0.1GHz"
        sweep.props["RangeEnd"] = "50GHz"
        sweep.props["SaveFields"] = False
        sweep.props["SaveRadFields"] = False
        sweep.props["Type"] = "Interpolating"
        sweep.update()

        self.q2d.save_project(os.path.join(work_dir, name))
        self.q2d.close_desktop()

    def create_differential_microstrip(self, name, work_dir):
        self.q2d[Var()._cond_h[0]] = "0.05mm"
        self.q2d[Var()._sig_w[0]] = "0.14mm"
        self.q2d[Var()._sig_gap[0]] = "0.15mm"
        self.q2d[Var()._clearance[0]] = "0.5mm"

        delta_w_half = "({0}/{1})".format(Var().cond_h, Var().etching)
        sig_top_w = "({1}-{0}*2)".format(delta_w_half, Var().sig_w)
        co_gnd_top_w = "({1}-{0})".format(delta_w_half, Var().co_gnd_w)

        ###############################################################################
        # Create primitives
        # ~~~~~~~~~~~~~~~~~
        # Create primitives and define the layer heights.

        layer_1_lh = 0
        layer_1_uh = Var().cond_h

        layer_2_lh = layer_1_uh + "+" + Var().diel_1_h
        layer_2_uh = layer_2_lh + "+" + Var().cond_h

        layer_air = layer_2_uh + "+" + Var().sm_h

        model_w = "{}*2+{}*2+{}*2+{}".format(Var().co_gnd_w, Var().clearance, Var().sig_w, Var().sig_gap)

        ###############################################################################
        # Create positive signal
        # ~~~~~~~~~~~~~~~~~~~~~~
        # Create a positive signal.

        base_line_obj = self.q2d.modeler.create_polyline([[0, layer_2_lh, 0], [Var().sig_w, layer_2_lh, 0]],
                                                         name="signal_p")
        top_line_obj = self.q2d.modeler.create_polyline([[0, layer_2_uh, 0], [sig_top_w, layer_2_uh, 0]])
        self.q2d.modeler.move([top_line_obj], [delta_w_half, 0, 0])
        self.q2d.modeler.connect([base_line_obj, top_line_obj])
        self.q2d.modeler.move([base_line_obj], ["{}+{}".format(Var().co_gnd_w, Var().clearance), 0, 0])

        # Create negative signal
        # ~~~~~~~~~~~~~~~~~~~~~~
        # Create a negative signal.

        base_line_obj = self.q2d.modeler.create_polyline([[0, layer_2_lh, 0], [Var().sig_w, layer_2_lh, 0]],
                                                         name="signal_n")
        top_line_obj = self.q2d.modeler.create_polyline([[0, layer_2_uh, 0], [sig_top_w, layer_2_uh, 0]])
        self.q2d.modeler.move([top_line_obj], [delta_w_half, 0, 0])
        self.q2d.modeler.connect([base_line_obj, top_line_obj])
        self.q2d.modeler.move([base_line_obj],
                              ["{}+{}+{}+{}".format(Var().co_gnd_w, Var().clearance, Var().sig_w, Var().sig_gap), 0, 0])

        ###############################################################################
        # Create coplanar ground
        # ~~~~~~~~~~~~~~~~~~~~~~
        # Create a coplanar ground.

        base_line_obj = self.q2d.modeler.create_polyline([[0, layer_2_lh, 0], [Var().co_gnd_w, layer_2_lh, 0]],
                                                         name="co_gnd_left")
        top_line_obj = self.q2d.modeler.create_polyline([[0, layer_2_uh, 0], [co_gnd_top_w, layer_2_uh, 0]])
        # self.q2d.modeler.move([top_line_obj], [delta_w_half, 0, 0])
        self.q2d.modeler.connect([base_line_obj, top_line_obj])

        base_line_obj = self.q2d.modeler.create_polyline([[0, layer_2_lh, 0], [Var().co_gnd_w, layer_2_lh, 0]],
                                                         name="co_gnd_right")
        top_line_obj = self.q2d.modeler.create_polyline([[0, layer_2_uh, 0], [co_gnd_top_w, layer_2_uh, 0]])
        self.q2d.modeler.move([top_line_obj], [delta_w_half, 0, 0])
        self.q2d.modeler.connect([base_line_obj, top_line_obj])
        self.q2d.modeler.move([base_line_obj],
                              ["{}+{}*2+{}*2+{}".format(Var().co_gnd_w, Var().clearance, Var().sig_w, Var().sig_gap), 0,
                               0])

        ###############################################################################
        # Create reference ground plane
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Create a reference ground plane.

        self.q2d.modeler.create_rectangle(position=[0, layer_1_lh, 0], dimension_list=[model_w, Var().cond_h],
                                          name="ref_gnd_l")

        ###############################################################################
        # Create dielectric
        # ~~~~~~~~~~~~~~~~~
        # Create a dielectric.

        self.q2d.modeler.create_rectangle(
            position=[0, layer_1_uh, 0], dimension_list=[model_w, Var().diel_1_h], name="Core", matname="my_fr4"
        )
        self.q2d.modeler.create_rectangle(
            position=[0, layer_2_uh, 0], dimension_list=[model_w, Var().sm_h], name="Sm", matname="Soldermask"
        )
        self.q2d.modeler.create_rectangle(
            position=[0, layer_air, 0], dimension_list=[model_w, "1mm"], name="air", matname="Air"
        )
        self.q2d.modeler.create_rectangle(
            position=[0, layer_2_lh, 0], dimension_list=[model_w, Var().cond_h], name="Filling", matname="Soldermask"
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

        # Create a setup.
        setup = self.q2d.create_setup(setupname="new_setup")

        # Add a sweep.
        sweep = setup.add_sweep(sweepname="sweep1", sweeptype="Discrete")
        sweep.props["RangeType"] = "LinearStep"
        sweep.props["RangeStart"] = "0.1GHz"
        sweep.props["RangeStep"] = "0.1GHz"
        sweep.props["RangeEnd"] = "50GHz"
        sweep.props["SaveFields"] = False
        sweep.props["SaveRadFields"] = False
        sweep.props["Type"] = "Interpolating"
        sweep.update()

        self.q2d.save_project(os.path.join(work_dir, name))
        self.q2d.close_desktop()


if __name__ == '__main__':
    """
    trans = TransLine2D()
    trans.create_differential_stripline("differential_stripline.aedt",
                                        r"C:\ansysdev\_aedt_workspace\pyaedt_pcb_design\q2d_transmissionline")
    """
    trans = TransLine2D()
    trans.create_differential_microstrip("differential_microstrip.aedt",
                                         r"C:\ansysdev\_aedt_workspace\pyaedt_pcb_design\q2d_transmissionline")
