import os

from pcb_design.base_2d import BaseQ2d


class Var:
    dk = ["$dk", 4]
    df = ["$dk", 0.005]
    ra = ["$ra", "0.2um"]
    sr = ["$sr", "5"]

    etching = ["etching", 2]
    x_limit_l = ["x_limit_l", "-1mm"]
    x_limit_r = ["x_limit_r", "1mm"]
    cond_h = "cond_h", "0.017mm"
    diel_1_h = "diel_1_h", "0.15mm"
    diel_2_h = "diel_2_h", "0.15mm"

    sig_w = "sig_w", "0.075mm"
    sig_gap = "sig_gap", "0.1mm"
    clearance = "clearance", "0.1mm"


class MicroStripSingle(BaseQ2d):
    def __init__(self, project_name ,work_dir):
        if work_dir:
            os.chdir(work_dir)

        BaseQ2d.__init__(project_name)

        self.init_variables(Var)





###############################################################################
# Save project and release AEDT
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Save the project and release AEDT.
q.save_project()
q.release_desktop()
