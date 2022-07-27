from utils.power_tree_schematic import PowerTreeTel
from utils.power_rail import PowerRail

PowerTreeTel.TP_PRIFIX = ["TP", "INC"]
PowerTreeTel.REPLACE_BY_RES = ["F"]
PowerTreeTel.CONNECTOR_PRIFIX = ["X", "J"]
PowerTreeTel.GROUND = ["GND"]
PowerTreeTel.COMP_EXCLUDE_LIST = ["EU1"]
PowerTreeTel.COMP_PIN_EXCLUDE_LIST = ["U2A5.E1"]

PowerTreeTel.EXCLUE_CONNECTOR = True

targetfile = r"galileo_example\galileo.tel"
print(targetfile)
PowerTreeTel(
    fpath=targetfile,
    bom="galileo_exmaple/bom_galileo.csv",
    power_rail_list=[
        PowerRail(
            prim_refdes_pin="U3A1.37", voltage=1.0,
            sec_refdes_pin_list=[],
            sink_power_info="galileo_example/U3A1-BST_V1P0_S0.csv"),

        PowerRail(prim_refdes_pin="U3A1.14", voltage=3.3),
    ],
    nexxim_sch=False
)
