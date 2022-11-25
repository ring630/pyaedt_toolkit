import os
import shutil
import itertools as it
import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd

from pyaedt import Desktop, Circuit, Edb

from . import log_info
from utils.configuration import PowerTreeConfig, IVComp
from utils.edb_to_tel import EdbToNetlist
from utils.netlist_process import NetList


class PowerTreeExtraction:
    _PWR_NETWORK = nx.Graph()
    _COMPONENTS = {}

    @property
    def power_network(self):
        if not len(self._PWR_NETWORK.nodes()):
            log_info("Building power network")
            self._PWR_NETWORK = nx.Graph()
            net_comp_ratlist = {}
            for i in self.netlist.core_components.get_rats():
                refdes = i["refdes"][0]
                pins = i["pin_name"]
                connected_nets = i["net_name"]

                node_names = [[refdes, n] for n in list(dict.fromkeys(connected_nets))]
                comp_all_nodes = []
                comp_type = ""
                for r, net_name in node_names:
                    pin = [pins[idx] for idx, n in enumerate(connected_nets) if n == net_name]
                    node_name = "-".join([r, net_name])

                    comp_type = self.netlist.core_components.components[r].type.lower()
                    self._PWR_NETWORK.add_node(node_name,
                                               pin_list=pin,
                                               refdes=r,
                                               net_name=net_name,
                                               comp_type=comp_type,
                                               )
                    comp_all_nodes.append(node_name)
                    if net_name not in net_comp_ratlist:
                        net_comp_ratlist[net_name] = [node_name]
                    else:
                        net_comp_ratlist[net_name].append(node_name)
                # add edge between RL pins
                if not self.netlist.core_components.components[refdes].is_enabled:
                    pass
                elif not len(comp_all_nodes) == 2:
                    pass
                elif comp_type in ["inductor", "resistor"]:
                    self._PWR_NETWORK.add_edge(*comp_all_nodes, net_name=comp_type.lower())

            # add edge between components
            for net_name, node_list in net_comp_ratlist.items():
                for comb in list(it.combinations(node_list, 2)):
                    self._PWR_NETWORK.add_edge(*comb, net_name=net_name)
            return self._PWR_NETWORK
        else:
            return self._PWR_NETWORK

    def __init__(self, project_dir, fname_cfg):
        self.default_cwd = os.getcwd()
        os.chdir(project_dir)
        self.netlist = None
        self.problematic_comp_list = []

        self.dcir_cfg = PowerTreeConfig(fname_cfg)

        self.fname_comp_definition = self.dcir_cfg.comp_definition
        self.fname_power_lib = self.dcir_cfg.power_lib_file

        self.edb_version = str(self.dcir_cfg.edb_version)
        self.edb_name = self.dcir_cfg.layout_file_name

    def extract_power_tree(self, aedt_nexxim=False, pdf_figsize=(36, 24)):
        # Create netlist
        netlist_name = self.edb_name.replace(".aedb", ".tel")
        if self.dcir_cfg.layout_file_name.endswith(".aedb"):


            if not os.path.isfile(netlist_name):
                log_info("Loading EDB layout.")
                edbapp = Edb(self.edb_name, edbversion=self.edb_version)
                lines = EdbToNetlist(edbapp).lines
                edbapp.close_edb()
                with open(netlist_name, "w") as f:
                    f.writelines(lines)
        else:
            log_info("Netlist already exists.")
        log_info("Loading netlist")
        self.netlist = NetList(netlist_name)
        if self.fname_comp_definition:
            self.netlist.import_comp_definition(self.fname_comp_definition)
        self.netlist.remove_capacitors()
        self.netlist.remove_resistor_by_value(self.dcir_cfg.resistor_removal_threshold)
        self.netlist.remove_comp_by_refdes(self.dcir_cfg.removal_list)
        self.netlist.remove_nets(self.dcir_cfg.gnd_net_name)

        # Create result folder
        self.output_folder = "extraction_result"
        if not os.path.isdir(self.output_folder):
            os.mkdir(self.output_folder)

        self._run(aedt_nexxim, pdf_figsize)
        self.export_problematic_comps(os.path.join(self.output_folder, "no_gnd_connect.csv"))
        os.chdir(self.default_cwd)
        log_info("Finished!")

    def _run(self, aedt_nexxim=False, pdf_figsize=(12, 8), ratio=0.3):

        graphs = {}
        for k, single_cfg in self.dcir_cfg.power_configs.items():
            sub_graph, single_cfg = self.build_power_tree(single_cfg)
            pos = nx.spring_layout(sub_graph, seed=100)
            graphs[k] = [sub_graph, pos]

        if self.fname_power_lib:
            self.dcir_cfg.import_power_lib(self.fname_power_lib)
        self.dcir_cfg.custom_comp_overwrite()
        #self.dcir_cfg.export_config_json(os.path.join(self.output_folder, self.edb_name.replace(".aedb", ".json")))
        #self.dcir_cfg.export_config_excel(os.path.join(self.output_folder, self.edb_name.replace(".aedb", ".xlsx")))
        self.dcir_cfg.export_config_json(os.path.join(self.output_folder, "configuration.json"))
        self.dcir_cfg.export_config_excel(os.path.join(self.output_folder, "configuration.xlsx"))

        for k, g in graphs.items():
            single_cfg = self.dcir_cfg.power_configs[k]
            sub_graph, pos = g
            self.visualize_power_tree_pdf(sub_graph, pos, single_cfg, pdf_figsize)

        if aedt_nexxim:
            non_graphical = True
            new_thread = True
            desktop = Desktop(self.edb_version, non_graphical, new_thread)
            for k, g in graphs.items():
                single_cfg = self.dcir_cfg.power_configs[k]
                sub_graph, pos = g
                self.visualize_power_tree_nexxim(sub_graph, pos, single_cfg, ratio=ratio*pdf_figsize[0]/12)

            #aedt_name = self.edb_name.replace(".aedb", ".aedt")
            aedt_name = "power_tree_in_nexxim.aedt"
            aedt_path = os.path.join(self.output_folder, aedt_name)
            edb_path = os.path.join(self.output_folder, self.edb_name)
            aedt_result_path = aedt_path.replace("aedt", "aedtresults")
            if os.path.isfile(aedt_path):
                os.remove(aedt_path)
            if os.path.isdir(edb_path):
                shutil.rmtree(edb_path)
            if os.path.isdir(aedt_result_path):
                shutil.rmtree(aedt_result_path)

            desktop.save_project(project_path=os.path.join(os.getcwd(), aedt_path))
            desktop.close_desktop()


    def build_power_tree(self, single_cfg):

        # Find primary source node name
        refdes = single_cfg.main_v_comp
        pin = str(single_cfg.main_v_comp_pin)
        for node_name, attr in self.power_network.nodes.data():
            if refdes == attr["refdes"] and pin in attr["pin_list"]:
                single_cfg._node_name = node_name
                k = list(single_cfg.v_comp.keys())[0]
                val = single_cfg.v_comp.pop(k)
                val.net_name = attr["net_name"]
                val.part_name = self.netlist.components[refdes].part_name
                val.pin_list = "-".join(attr["pin_list"])
                single_cfg.v_comp[node_name] = val
                break

        # Find power rail network
        prim_node = single_cfg._node_name
        sub_graph = None
        for i in nx.connected_components(self.power_network):
            if prim_node in i:
                sub_graph = self.power_network.subgraph(i)
                _nets = list(set(nx.get_edge_attributes(sub_graph, "net_name").values()))
                _nets = [i for i in _nets if i not in ["resistor", "inductor"]]
                _nets = [i for i in _nets if i not in self.dcir_cfg.all_power_nets]
                self.dcir_cfg.all_power_nets.extend(_nets)
                break
        sub_graph = nx.create_empty_copy(sub_graph)

        for node_name, attr in sub_graph.nodes.data():
            if node_name == prim_node:
                sub_graph.nodes[node_name]["dcir_type"] = "source"
                sub_graph.nodes[node_name]["voltage"] = single_cfg.voltage

            elif sub_graph.nodes[node_name]["comp_type"] in ["resistor", "inductor"]:
                sub_graph.nodes[node_name]["dcir_type"] = "dc_comp"
            else:
                sub_graph.nodes[node_name]["dcir_type"] = "sink"
                sub_graph.nodes[node_name]["current"] = 0.001
                refdes = attr["refdes"]

                comp = self.netlist.components[refdes]
                if self.dcir_cfg.gnd_net_name not in  [p.net_name for p in comp.pins]:
                    self.problematic_comp_list.append(refdes)

                i_comp = IVComp(refdes,
                                part_name=comp.part_name,
                                net_name=attr["net_name"],
                                pin_list="-".join(attr["pin_list"]),
                                value=0.001
                                )
                i_comp._node_name = node_name
                single_cfg.i_comp[node_name] = i_comp

        # connect RLC terminals again
        edge_list = {}
        for node_name, attr in sub_graph.nodes.data():
            if attr["comp_type"] not in ["resistor", "inductor"]:
                continue
            else:
                refdes = attr["refdes"]
                for n in self.power_network.adj[node_name]:
                    if sub_graph.nodes[n]["refdes"] == refdes:
                        if refdes not in edge_list:
                            edge_list[refdes] = [node_name, n]
        for refdes, edge in edge_list.items():
            sub_graph.add_edge(*edge, net_name="DC_COMP")

        # Create chain like network
        node_list = {}
        for node_name, attr in sub_graph.nodes.data():
            net_name = attr["net_name"]
            if net_name not in node_list:
                node_list[net_name] = {"dc_comp": [], "sink": []}

            if attr["comp_type"] in ["resistor", "inductor"]:
                node_list[net_name]["dc_comp"].append(node_name)
            elif node_name == single_cfg._node_name:
                node_list[net_name]["dc_comp"].append(node_name)
            else:
                node_list[net_name]["sink"].append(node_name)

        for net_name, attr in node_list.items():
            if net_name not in sub_graph.nodes():
                # add net_name node
                sub_graph.add_node(net_name, dcir_type="net", refdes=net_name)

            for dc_comp in attr["dc_comp"]:
                sub_graph.add_edge(net_name, dc_comp, net_name=net_name)

            last_node = None
            for idx, sink in enumerate(attr["sink"]):
                if idx == 0:
                    sub_graph.add_edge(net_name, sink, net_name=net_name)
                    last_node = sink
                else:
                    sub_graph.add_edge(last_node, sink, net_name=net_name)
                    last_node = sink

        # Merge DC COMP nodes
        node_removal_list = []
        for n1, n2, attr in sub_graph.edges.data():
            if attr["net_name"] == "DC_COMP":
                new_node_name = "{}-{}".format(n1.split("-")[1], n2)
                node_removal_list.append([n1, n2, new_node_name])
        for i in node_removal_list:
            n1, n2, new_node_name = i
            sub_graph.add_node(new_node_name, dcir_type="dc_comp", refdes=sub_graph.nodes[n1]["refdes"],
                               net_name=[sub_graph.nodes[n1]["net_name"], sub_graph.nodes[n2]["net_name"]])
            for n in sub_graph.adj[n1]:
                if not n == n2:
                    sub_graph.add_edge(new_node_name, n)
            for n in sub_graph.adj[n2]:
                if not n == n1:
                    sub_graph.add_edge(new_node_name, n)
            sub_graph.remove_node(n1)
            sub_graph.remove_node(n2)

        return sub_graph, single_cfg

    def visualize_power_tree_pdf(self, graph, pos, cfg, figsize, plot=False):
        node_color = []
        node_size = []
        for n, _ in graph.nodes.data():
            if graph.nodes[n]["dcir_type"] == "source":
                node_size.append(300)
                node_color.append("r")
            elif graph.nodes[n]["dcir_type"] == "sink":
                node_size.append(150)
                node_color.append("g")
            elif graph.nodes[n]["dcir_type"] == "net":
                node_size.append(1)
                node_color.append("y")
            else:
                node_size.append(20)
                node_color.append("y")

        fig, ax = plt.subplots(figsize=figsize)
        nx.draw_networkx_nodes(graph, pos=pos, ax=ax, node_shape=".",
                               node_color=node_color,
                               node_size=node_size)
        nx.draw_networkx_edges(graph, pos,
                               ax=ax,
                               arrows=True,
                               min_source_margin=0,
                               min_target_margin=0
                               )
        for n, p in pos.items():
            x, y = p
            attr = graph.nodes.data()[n]
            refdes = attr["refdes"]
            if attr["dcir_type"] == "sink":
                part_name = self.netlist.core_components.components[refdes].part_name
                current = cfg.i_comp[n].value
                txt = "{}\n{}\nCurrent={}\n".format(refdes, part_name, current)
                ax.text(x, y, txt, color="g", fontsize=20, horizontalalignment="left")

            elif attr["dcir_type"] == "source":
                txt = "{}\nVoltage={}\n".format(refdes, attr["voltage"])
                ax.text(x, y, txt, color="r", fontsize=20, horizontalalignment="left")

            elif attr["dcir_type"] == "net":
                txt = "{}".format(refdes)
                ax.text(x, y, txt, fontsize=12, horizontalalignment="center")

            else:
                comp = self.netlist.components[refdes]
                txt = "{}-{}".format(refdes, comp.value)
                ax.text(x, y, txt, fontsize=12, horizontalalignment="left",
                        bbox=dict(facecolor='none', edgecolor='black', pad=2.0))

        png_fpath = os.path.join(self.output_folder, cfg._node_name + ".png")
        plt.tight_layout()
        plt.savefig(png_fpath)
        if plot:
            plt.show()
        plt.close()

    def visualize_power_tree_nexxim(self, G, pos, cfg, ratio=0.15):

        #non_graphical = os.getenv("PYAEDT_NON_GRAPHICAL", "False").lower() in ("true", "1", "t")

        cir = Circuit(designname=cfg._node_name.replace("-", "_"))

        for node_name, p in pos.items():
            x, y = p * ratio
            dcir_type = G.nodes[node_name]["dcir_type"]
            comp_name = node_name.replace("-", "_")
            if comp_name[0].isdigit():
                comp_name = "_" + comp_name

            if dcir_type == "net":
                pass
            elif dcir_type == "dc_comp":
                if G.degree[node_name] < 2:
                    continue
                refdes = G.nodes[node_name]["refdes"]
                comp = self.netlist.components[refdes]
                value = comp.value if not comp.type.capitalize() == "Inductor" else 0
                res = cir.modeler.schematic.create_resistor(comp_name, value, [x, y])
                n1, n2 = G.nodes[node_name]["net_name"]
                cir.modeler.components.create_page_port(n1, res.pins[0].location, angle=180)
                cir.modeler.components.create_page_port(n2, res.pins[1].location)

            else:
                try:
                    refdes, net_name = node_name.split("-")
                except:
                    refdes = node_name.split("-")[0]
                    net_name = node_name.split("-")[1:]

                if dcir_type == "source":
                    voltage = cfg.voltage
                    source = cir.modeler.schematic.create_voltage_dc(comp_name, voltage, [x, y])
                    cir.modeler.components.create_page_port(net_name, source.pins[1].location)
                    cir.modeler.components.create_page_port("0", source.pins[0].location)
                else:

                    current = cfg.i_comp[node_name].value
                    sink = cir.modeler.schematic.create_current_dc(comp_name, current, [x, y])
                    cir.modeler.components.create_page_port(net_name, sink.pins[1].location)
                    cir.modeler.components.create_page_port("0", sink.pins[0].location)
                    cir.modeler.components.create_voltage_probe(comp_name, sink.pins[1].location)

        for e in G.edges:
            u, v = e
            p1 = [i * ratio for i in pos[u]]
            p2 = [i * ratio for i in pos[v]]

            if G.nodes[u]["dcir_type"] == "source" or G.nodes[v]["dcir_type"] == "source":
                color = 255
            else:
                color = 0
            cir.modeler.components.create_line([p1, p2], color)

    def export_problematic_comps(self, file_path):
        pd.Series(self.problematic_comp_list).to_csv(file_path)


