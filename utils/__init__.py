import time
import os
import tempfile
import shutil
from pyaedt import generate_unique_name, examples


def str2float(des_type, val):
    if isinstance(val, float):
        return val
    if isinstance(val, int):
        return val
    if val.endswith("M"):
        val = val + "EG"

    val = val.lower()
    val = val.replace(",", ".")

    removal_list = ["ohm", "ohms"]

    res_value_dict = {"m": "e-3",
                      "k": "e3",
                      "meg": "e6"
                      }
    if des_type == "resistor":
        for i in removal_list:
            if val.endswith(i):
                val = val.replace(i, "")

        for i, j in res_value_dict.items():
            if val.endswith(i):
                val = val.replace(i, j)
    return float(val)


def log_info(name):
    print(time.ctime(), name)


def get_galileo_exmaple_board():
    tmpfold = tempfile.gettempdir()
    temp_folder = os.path.join(tmpfold, generate_unique_name("Example"))
    if not os.path.exists(temp_folder):
        os.makedirs(temp_folder)
    example_path = examples.download_aedb()
    targetfolder = os.path.join(temp_folder, "Galileo.aedb")
    if os.path.exists(targetfolder):
        shutil.rmtree(targetfolder)
    shutil.copytree(example_path[:-8], targetfolder)
    targetfile = os.path.join(targetfolder)
    return targetfile