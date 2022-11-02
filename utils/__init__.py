import time

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