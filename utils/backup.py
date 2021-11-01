    """
        def _load_user_configuration(self):
    self.user_configuration.load_dcir_cfg()

def _export_library_to_be_filled(self):
    self.library_to_be_filled.export_library(file_name="library_to_be_filled.json")

def _import_library(self):
    self.library.import_library()

def _refresh_library(self):
    self.library.import_library()
    self.library_to_be_filled.import_library(file_name="library_to_be_filled.json")
    comp_to_remove = []
    for part_name, comp in self.library_to_be_filled.components.items():
        comp_filled = copy(comp)
        for name, p in comp.power_rails.items():
            if not p["current"]:
                del comp_filled.power_rails[name]
        if len(comp_filled.power_rails):
            comp_to_remove.append(part_name)
            if part_name in self.library.components:
                comp_temp = self.library.components[part_name]
                comp_temp.power_rails = {**comp_temp.power_rails, **comp_filled.power_rails}
                print("add new power rails to existing component {}".format(part_name))
            else:
                self.library.add_component(comp_filled)
                print("add new components {}".format(part_name))

    for i in comp_to_remove:
        del self.library_to_be_filled.components[i]
    self.library_to_be_filled.export_library(file_name="library_to_be_filled.json")
    self.library.export_library()
    """


    def ___(self):
        self.app_power_tree.config_dcir(sink_source_cfg, ref_net_name=user_config.reference_net_name)
        signal_list.extend(sink_source_cfg.net_group)

        self.new_component.export_library(file_name="library_to_be_filled.json")

        if cutout:
            self.app_power_tree.cutout(user_config.reference_net_name, signal_list)

        self.app_power_tree.add_siwave_dc_analysis("DCIR", node_to_ground=self.node_to_ground,
                                                   accuracy_level=1)
        new_aedb_path = self.save_aedt_as.replace(".aedt", ".aedb")
        self.app_power_tree.save_edb_as(new_aedb_path)
        self.app_power_tree.create_aedt_project(new_aedb_path, DCIR_setup_name="DCIR", solve=solve)

        # self._config_dcir(user_configuration=user_config, solve=solve)
        # self._wrtie_results_to_json()


    """if sink_source_cfg.refdes == user_config.node_to_ground:
            self.node_to_ground.append(sink_source_cfg.cfg_id)
    
        for sink_id, sink in sink_source_cfg.sinks.items():
            if sink.part_name in self.library.components:
                power_rail_name = self.library.get_power_rail_name_from_pins(sink.part_name, sink.pins)
                if power_rail_name:
                    sink.current = self.library.get_current(part_name=sink.part_name,
                                                            power_rail_name=power_rail_name)
                    print(sink.current)
                    continue
    
            comp = Component(sink.part_name)
            comp.add_power_rail(sink.sink_id, sink.pins, current=0)
            self.new_component.add_component(comp)"""

"""class Library:

    def __init__(self):
        self.components = {}

    def add_component(self, component=Component()):
        self.components[component.part_name] = component

    def get_current(self, part_name, power_rail_name):
        if power_rail_name:
            return self.components[part_name].power_rails[power_rail_name]["current"]
        return False

    def get_power_rail_name_from_pins(self, part_name, pins):
        for name, i in self.components[part_name].power_rails.items():
            if not i["pins"] == pins:
                continue
            else:
                return name
        return False

    def create_example_library(self, path=""):

        comp = Component("IPD031-201")
        comp.add_power_rail("Core_1V0", "Y14-AB14-AD14-V14-Y20-Y18-Y16-AB20-AB18-T18-V20-V18-V16", 10)
        self.components["IPD031-201"] = comp

        comp = Component("E17764-001")
        comp.add_power_rail("P1V0", "10", 1)
        self.components["E17764-001"] = comp

        self.export_library(path, backup=True)

    def export_library(self, path="", file_name="library.json", backup=False, backup_dir="log"):
        exp = {}
        for part_name, comp in self.components.items():
            exp[part_name] = comp.__dict__

        fpath = os.path.join(path, file_name)
        if os.path.isfile(fpath):
            if backup:
                if not os.path.isdir(backup_dir):
                    os.mkdir(backup_dir)
                current_time = datetime.now().strftime("%y%m%d-%H-%M-%S")
                shutil.copyfile(fpath, os.path.join(backup_dir, "{}-{}".format(fpath, current_time)))

        with open(fpath, "w", encoding="utf-8") as f:
            f.write(json.dumps(exp, indent=4))

    def import_library(self, fpath):
        self.components = {}
        with open(fpath, "r") as f:
            json_obj = json.load(f)
            for part_name, comp in json_obj.items():
                comp_tmp = Component()
                for k, v in comp.items():
                    comp_tmp.__dict__[k] = v
                self.components[part_name] = comp_tmp
        return"""