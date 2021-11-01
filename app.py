from utils.dcir_workflow import DcirAutomation

dcir = DcirAutomation(layout_file=r"layout_database\Galileo.aedb",
                      edb_version="2021.2"
                      )

dcir.extract_power_tree(
    sources=[{"refdes": "U3A1", "voltage": 1, "o_net_name": "BST_V1P0_S0", "o_inductor_refdes": None},
             {"refdes": "U3A1", "voltage": 3.3, "o_net_name": None, "o_inductor_refdes": "L3A1"},
             ],
    ref_net_name="GND",
)
dcir.config_dcir(node_to_ground="U3A1", solve= False)