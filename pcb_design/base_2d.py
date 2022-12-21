import os

from pyaedt import Q2d


class BaseQ2d:
    def __init__(self, project_name):
        non_graphical = os.getenv("PYAEDT_NON_GRAPHICAL", "False").lower() in ("true", "1", "t")
        self.q2d = Q2d(projectname=project_name, designname="differential_stripline",
                specified_version="2022.2", non_graphical=non_graphical, new_desktop_session=True)
        
    def init_variables(self, vars):
        for name, val in vars.__dict__.items():
            self.q2d[name] = val
    
    def init_materials(self):
        my_mat = self.q2d.materials.add_material("my_fr4")
        my_mat.permittivity = "$dk"
        my_mat.dielectric_loss_tangent = "$df"

    def create_board(self, vars, layer_count=2):
        delta_w_half = "({0}/{1})".format(vars.cond_h, vars.etching)
        sig_top_w = "({1}-{0}*2)".format(delta_w_half, vars.sig_w)

        ###############################################################################
        # Create primitives
        # ~~~~~~~~~~~~~~~~~
        # Create primitives and define the layer heights.

        layer_1_lh = 0
        layer_1_uh = vars.cond_h
        layer_2_lh = layer_1_uh + "+" + vars.core_h
        layer_2_uh = layer_2_lh + "+" + vars.cond_h
        layer_3_lh = layer_2_uh + "+" + vars.
        layer_3_uh = layer_3_lh + "+" + cond_h

        ###############################################################################
        # Create positive signal
        # ~~~~~~~~~~~~~~~~~~~~~~
        # Create a positive signal.

        base_line_obj = self.q2d.modeler.create_polyline([[0, layer_2_lh, 0], [sig_w, layer_2_lh, 0]], name="signal_p")
        top_line_obj = self.q2d.modeler.create_polyline([[0, layer_2_uh, 0], [sig_top_w, layer_2_uh, 0]])
        self.q2d.modeler.move([top_line_obj], [delta_w_half, 0, 0])
        self.q2d.modeler.connect([base_line_obj, top_line_obj])
        self.q2d.modeler.move([base_line_obj], ["{}+{}".format(co_gnd_w, clearance), 0, 0])

        # Create negative signal
        # ~~~~~~~~~~~~~~~~~~~~~~
        # Create a negative signal.

        base_line_obj = self.q2d.modeler.create_polyline([[0, layer_2_lh, 0], [sig_w, layer_2_lh, 0]], name="signal_n")
        top_line_obj = self.q2d.modeler.create_polyline([[0, layer_2_uh, 0], [sig_top_w, layer_2_uh, 0]])
        self.q2d.modeler.move([top_line_obj], [delta_w_half, 0, 0])
        self.q2d.modeler.connect([base_line_obj, top_line_obj])
        self.q2d.modeler.move([base_line_obj], ["{}+{}+{}+{}".format(co_gnd_w, clearance, sig_w, sig_gap), 0, 0])
        """
        ###############################################################################
        # Create coplanar ground
        # ~~~~~~~~~~~~~~~~~~~~~~
        # Create a coplanar ground.

        base_line_obj = self.q2d.modeler.create_polyline([[0, layer_2_lh, 0], [co_gnd_w, layer_2_lh, 0]], name="co_gnd_left")
        top_line_obj = self.q2d.modeler.create_polyline([[0, layer_2_uh, 0], [co_gnd_top_w, layer_2_uh, 0]])
        self.q2d.modeler.move([top_line_obj], [delta_w_half, 0, 0])
        self.q2d.modeler.connect([base_line_obj, top_line_obj])

        base_line_obj = self.q2d.modeler.create_polyline([[0, layer_2_lh, 0], [co_gnd_w, layer_2_lh, 0]], name="co_gnd_right")
        top_line_obj = self.q2d.modeler.create_polyline([[0, layer_2_uh, 0], [co_gnd_top_w, layer_2_uh, 0]])
        self.q2d.modeler.move([top_line_obj], [delta_w_half, 0, 0])
        self.q2d.modeler.connect([base_line_obj, top_line_obj])
        self.q2d.modeler.move([base_line_obj], ["{}+{}*2+{}*2+{}".format(co_gnd_w, clearance, sig_w, sig_gap), 0, 0])
        """
        ###############################################################################
        # Create reference ground plane
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Create a reference ground plane.

        self.q2d.modeler.create_rectangle(position=[0, layer_1_lh, 0], dimension_list=[model_w, cond_h], name="ref_gnd_u")
        self.q2d.modeler.create_rectangle(position=[0, layer_3_lh, 0], dimension_list=[model_w, cond_h], name="ref_gnd_l")

        ###############################################################################
        # Create dielectric
        # ~~~~~~~~~~~~~~~~~
        # Create a dielectric.

        self.q2d.modeler.create_rectangle(
            position=[0, layer_1_uh, 0], dimension_list=[model_w, core_h], name="Core", matname="FR4_epoxy"
        )
        self.q2d.modeler.create_rectangle(
            position=[0, layer_2_uh, 0], dimension_list=[model_w, pp_h], name="Prepreg", matname="FR4_epoxy"
        )
        self.q2d.modeler.create_rectangle(
            position=[0, layer_2_lh, 0], dimension_list=[model_w, cond_h], name="Filling", matname="FR4_epoxy"
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
        # Reference the ground.

        # obj = [self.q2d.modeler.get_object_from_name(i) for i in ["co_gnd_left", "co_gnd_right", "ref_gnd_u", "ref_gnd_l"]]
        obj = [self.q2d.modeler.get_object_from_name(i) for i in ["ref_gnd_u", "ref_gnd_l"]]
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

        matrix = self.q2d.insert_reduced_matrix(self.q2d.MATRIXOPERATIONS.DiffPair, ["signal_p", "signal_n"], rm_name="diff_pair")

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

    def save_edb_and_close(self, aedb_name):
        pass