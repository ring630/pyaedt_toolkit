from utils.dcir_workflow import DcirWorkflow

app_dcir = DcirWorkflow()
app_dcir.extract_power_tree()
#app_dcir.refresh_library()
app_dcir.analyze()