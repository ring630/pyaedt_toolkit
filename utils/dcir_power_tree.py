import os
import itertools as it
import shutil
import re
import tempfile
import matplotlib.pyplot as plt
import networkx as nx
from pyaedt import Desktop, Circuit
from .power_rail import str2float, Sink
from utils.power_rail import PowerRail


class DCIRPowerTree:
    EDB_VERSION = None
    DEFAULT_SINK_CURRENT = 0.001

    TP_PRIFIX = ["TP"]

    EXCLUE_CONNECTOR = False
    CONNECTOR_PRIFIX = ["X"]
    REPLACE_BY_RES = ["F"]

    DC_COMP_TYPE = ["resistor", "inductor"]

    GROUND = ["GND"]
    COMP_EXCLUDE_LIST = []
    COMP_PIN_EXCLUDE_LIST = []

    _PWR_NETWORK = nx.Graph()
    _COMPONENTS = {}

    @property
    def components(self):
        return self.edb.core_components.components

    @property
    def power_network(self):
        if not len(self._PWR_NETWORK.nodes()):
            self._PWR_NETWORK = nx.Graph()
            net_comp_ratlist = {}
            for i in self.edb.core_components.get_rats():
                refdes = i["refdes"][0]
                pins = i["pin_name"]
                connected_nets = i["net_name"]

                node_names = [[refdes, n] for n in list(dict.fromkeys(connected_nets))]
                comp_all_nodes = []
                comp_type = ""
                for r, net_name in node_names:
                    pin = [pins[idx] for idx, n in enumerate(connected_nets) if n == net_name]
                    node_name = "-".join([r, net_name])

                    comp_type = self.edb.core_components.components[r].type.lower()
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
                if not self.edb.core_components.components[refdes].is_enabled:
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

    def __init__(self, edb, edb_version):
        self.EDB_VERSION = edb_version
        self.edb = edb
        self.dcir_config_list = []

        if not os.path.isdir("temp"):
            os.mkdir("temp")
        print("Number of components {}".format(len(self.edb.core_components.components)))

        self.power_rail_list = []

    def add_power_rail(self,
                       refdes_pin,
                       voltage=1.2,
                       sense_pin=None,
                       sink_power_info="",
                       node_to_ground=True,
                       ):
        power_rail = PowerRail(refdes_pin,
                               voltage,
                               sense_pin,
                               sink_power_info,
                               node_to_ground)
        self.power_rail_list.append(power_rail)
        pass

    def run(self, pdf_or_aedt="pdf"):
        # edb update
        #self._replace_comp_with_resistor_from_edb()

        # power tree network creation
        #self._remove_node_to_ground_from_tree()
        #self._remove_test_points_from_tree()

        #if self.EXCLUE_CONNECTOR:
        #    self._remove_connectors_from_tree()

        #self._remove_excluded_components_from_tree()
        #self._remove_excluded_component_pins_from_tree()
        #self._remove_capacitors_from_tree()
        #self._remove_resistors_from_tree()

        for power_rail in self.power_rail_list:
            sub_graph, power_rail = self.build_power_tree(power_rail)
            power_rail.export_sink_info()
            power_rail.import_sink_info()

            pos = nx.spring_layout(sub_graph, seed=100)
            if pdf_or_aedt == "pdf":
                self.visualize_power_tree_pdf(sub_graph, pos, power_rail)
            else:
                self.visualize_power_tree_nexxim(sub_graph, pos, power_rail)
            self.dcir_config_list.append(power_rail)

    """def _remove_node_to_ground_from_tree(self):
        remove_list = []
        for node_name, data in self.power_network.nodes.data():
            if data["net_name"] in self.GROUND:
                remove_list.append(node_name)
        for i in remove_list:
            self.power_network.remove_node(i)

    def _replace_comp_with_resistor_from_edb(self):
        remove_list = []
        for node_name, data in self.power_network.nodes.data():
            if re.match("({}).*$".format("|".join(self.TP_PRIFIX)), data["refdes"]):
                remove_list.append(node_name)
        for i in remove_list:
            self.power_network.remove_node(i)
        # self.REPLACE_BY_RES

    def _remove_capacitors_from_tree(self):
        remove_list = []
        for node_name, data in self.power_network.nodes.data():
            if data["comp_type"] == "capacitor":
                remove_list.append(node_name)
        for i in remove_list:
            self.power_network.remove_node(i)

    def _remove_resistors_from_tree(self, threshold=10):
        remove_list = []
        for node_name, data in self.power_network.nodes.data():
            if data["comp_type"] == "resistor":
                refdes = data["refdes"]
                if str2float("resistor", self.edb.core_components.components[refdes].res_value) > threshold:
                    remove_list.append(node_name)
        for i in remove_list:
            self.power_network.remove_node(i)

    def _remove_test_points_from_tree(self):
        remove_list = []
        for node_name, data in self.power_network.nodes.data():
            if re.match("({}).*$".format("|".join(self.TP_PRIFIX)), data["refdes"]):
                remove_list.append(node_name)
        for i in remove_list:
            self.power_network.remove_node(i)

    def _remove_connectors_from_tree(self):
        remove_list = []
        for node_name, data in self.power_network.nodes.data():
            if re.match("({}).*$".format("|".join(self.CONNECTOR_PRIFIX)), data["refdes"]):
                remove_list.append(node_name)
        for i in remove_list:
            self.power_network.remove_node(i)

    def _remove_excluded_components_from_tree(self):
        remove_list = []
        for node_name, data in self.power_network.nodes.data():
            if data["refdes"] in self.COMP_EXCLUDE_LIST:
                remove_list.append(node_name)
        for i in remove_list:
            self.power_network.remove_node(i)

    def _remove_excluded_component_pins_from_tree(self):
        remove_list = []
        for comp_pin in self.COMP_PIN_EXCLUDE_LIST:
            refdes, pin = comp_pin.split(".")
            for node_name, data in self.power_network.nodes.data():
                if data["refdes"] == refdes:
                    if pin in data["pin_list"]:
                        remove_list.append(node_name)
        for i in remove_list:
            self.power_network.remove_node(i)"""

    def build_power_tree(self, power_rail):

        # Find primary source node name
        refdes_pin = power_rail._refdes_pin
        refdes, pin = refdes_pin.split(".")
        for node_name, attr in self.power_network.nodes.data():
            if refdes == attr["refdes"] and pin in attr["pin_list"]:
                power_rail._node_name = node_name
        """
        # Find secondary source node name
        for i in power_rail.sec_refdes_pin_list:
            refdes, pin = i.split(".")
            for node_name, attr in self.power_network.nodes.data():
                if refdes == attr["refdes"] and pin in attr["pin_list"]:
                    power_rail.sec_node_name_list.append(node_name)
        """
        # Find power rail network
        prim_node = power_rail._node_name
        sub_graph = None
        for i in nx.connected_components(self.power_network):
            if prim_node in i:
                sub_graph = self.power_network.subgraph(i)
                break
        sub_graph = nx.create_empty_copy(sub_graph)

        for node_name, attr in sub_graph.nodes.data():
            if node_name == prim_node:
                sub_graph.nodes[node_name]["dcir_type"] = "source"
                sub_graph.nodes[node_name]["voltage"] = power_rail.voltage

            #elif node_name in power_rail.sec_refdes_pin_list:
                #sub_graph.nodes[node_name]["dcir_type"] = "source"
                #sub_graph.nodes[node_name]["voltage"] = power_rail.voltage

            elif sub_graph.nodes[node_name]["comp_type"] in self.DC_COMP_TYPE:
                sub_graph.nodes[node_name]["dcir_type"] = "dc_comp"
            else:
                sub_graph.nodes[node_name]["dcir_type"] = "sink"
                sub_graph.nodes[node_name]["current"] = 0.001
                refdes = attr["refdes"]
                power_rail.sinks[node_name] = Sink(refdes=refdes,
                                                   part_name=self.components[refdes].partname,
                                                   net_name=attr["net_name"],
                                                   pin_list=attr["pin_list"],
                                                   node_name=node_name,
                                                   current=self.DEFAULT_SINK_CURRENT)

        # connect RLC terminals again
        edge_list = {}
        for node_name, attr in sub_graph.nodes.data():
            if attr["comp_type"] not in self.DC_COMP_TYPE:
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

            if attr["comp_type"] in self.DC_COMP_TYPE:
                node_list[net_name]["dc_comp"].append(node_name)
            elif node_name == power_rail._node_name:
                node_list[net_name]["dc_comp"].append(node_name)
            else:
                node_list[net_name]["sink"].append(node_name)

        # Adjust secondary source if applicable
        # Connect prim and sec sources
        #for node_name in power_rail.sec_node_name_list:
        #    sub_graph.nodes[node_name]["dcir_type"] = "source"
        #    sub_graph.nodes[node_name]["voltage"] = power_rail.voltage
        #    sub_graph.add_edge(power_rail._node_name, node_name, net_name="multi_phase")

        for net_name, attr in node_list.items():
            if net_name not in sub_graph.nodes():
                # add net_name node
                sub_graph.add_node(net_name, dcir_type="net", refdes=net_name)

            for dc_comp in attr["dc_comp"]:
                sub_graph.add_edge(net_name, dc_comp, net_name=net_name)

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
                               net_name=[sub_graph.nodes[n1]["net_name"], sub_graph.nodes[n1]["net_name"]])
            for n in sub_graph.adj[n1]:
                if not n == n2:
                    sub_graph.add_edge(new_node_name, n)
            for n in sub_graph.adj[n2]:
                if not n == n1:
                    sub_graph.add_edge(new_node_name, n)
            sub_graph.remove_node(n1)
            sub_graph.remove_node(n2)

        return sub_graph, power_rail

    def visualize_power_tree_pdf(self, graph, pos, power_rail):
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

        fig, ax = plt.subplots(figsize=(12, 8))
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
                part_name = self.components[refdes].partname
                current = power_rail.sinks[n].current
                txt = "{}\n{}\nCurrent={}\n".format(refdes, part_name, current)
                ax.text(x, y, txt, color="g", fontsize=10, horizontalalignment="left")

            elif attr["dcir_type"] == "source":
                txt = "{}\nVoltage={}\n".format(refdes, attr["voltage"])
                ax.text(x, y, txt, color="r", fontsize=10, horizontalalignment="left")

            elif attr["dcir_type"] == "net":
                txt = "{}".format(refdes)
                ax.text(x, y, txt, fontsize=6, horizontalalignment="center")

            else:
                txt = "{}".format(refdes)
                ax.text(x, y, txt, fontsize=6, horizontalalignment="left",
                        bbox=dict(facecolor='none', edgecolor='black', pad=2.0))

        png_fpath = os.path.join("temp", power_rail.figure_save_name)
        plt.tight_layout()
        plt.savefig(png_fpath)
        plt.show()
        print("* Save power tree png to", os.path.join("temp", power_rail.figure_save_name))

    def visualize_power_tree_nexxim(self, G, pos, power_rail, ratio=0.15):

        non_graphical = os.getenv("PYAEDT_NON_GRAPHICAL", "False").lower() in ("true", "1", "t")
        new_thread = False
        Desktop(self.EDB_VERSION, non_graphical, new_thread)
        cir = Circuit(designname=power_rail._node_name)

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
                res = cir.modeler.schematic.create_resistor(comp_name, 0.001, [x, y])
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
                    voltage = power_rail.voltage
                    source = cir.modeler.schematic.create_voltage_dc(comp_name, voltage, [x, y])
                    cir.modeler.components.create_page_port(net_name, source.pins[1].location)
                    cir.modeler.components.create_page_port("0", source.pins[0].location)
                else:
                    current = power_rail.sinks[node_name].current
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

    def close_aedt(self):
        non_graphical = os.getenv("PYAEDT_NON_GRAPHICAL", "False").lower() in ("true", "1", "t")
        new_thread = False
        destop = Desktop(self.EDB_VERSION, non_graphical, new_thread)
        destop.release_desktop()