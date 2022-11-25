import os


class ExampleBoard:

    def __init__(self):
        self.exmaple_board_folder = r"C:\Users\hzhou\OneDrive - ANSYS, Inc\example_board"
        self.edb_file = {
            "nokia_huge_board": r"nokia_huge_board\EDB_2022R2_986909x4_final.tgz.aedb",
            "intel_galileo": r"intel_galileo\Galileo.aedb"
        }

    @property
    def temp_foler(self):
        return r"C:\Users\hzhou\AppData\Roaming\JetBrains\PyCharmCE2022.1\scratches\temp_files"

    @property
    def nokia_huge_board(self):
        return os.path.join(self.exmaple_board_folder, self.edb_file["nokia_huge_board"])

    @property
    def intel_galileo(self):
        return os.path.join(self.exmaple_board_folder, self.edb_file["intel_galileo"])