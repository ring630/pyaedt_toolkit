from .power_tree_base import PowerTreeBase
from pyaedt import Edb


class PowerTreeEdb(PowerTreeBase):

    def __init__(self, fpath, power_rail_list, bom="", nexxim_sch=False):
        self.edb_path = fpath
        self.appedb = Edb(fpath, edbversion=self.EDB_VERSION)
        PowerTreeBase.__init__(self, power_rail_list, bom, nexxim_sch)
