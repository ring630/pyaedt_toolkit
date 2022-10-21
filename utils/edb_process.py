from pyaedt import Edb


class EdbLayout:

    def __init__(self, fpath, edb_version):
        self.edbapp = Edb(fpath, edbversion=edb_version)

    def import_comp_definition(self, fpath):
        self.edbapp.core_components.import_definition(fpath)

    def config_iv_comp(self, main_node, v_comp_list):
        pass
