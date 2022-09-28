from pyaedt import Edb
from .get_galileo_example_board import get_galileo_exmaple_board

class EdbPreprocessing:

    def __init__(self, fpath, edb_version):
        self.appedb = Edb(fpath, edbversion=edb_version)

    def load_bom(self, bom_file):
        self.appedb.core_components.update_rlc_from_bom(bom_file, delimiter=",")

if __name__ == '__main__':
    edb_file = get_galileo_exmaple_board()
    app = EdbPreprocessing(edb_file, "2022.2")
    app.load_bom("bom.csv")