import os

print(os.getcwd())
from utils.dcir_workflow import DcirWorkflow

app_workflow = DcirWorkflow()
app_workflow.run()


