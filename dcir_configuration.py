import os
from utils.dcir_analysis import DCIRAnalysis

import tkinter as tk
from tkinter import filedialog

root = tk.Tk()
root.withdraw()

file_path = filedialog.askopenfilename()
project_dir = os.path.dirname(file_path)
project_dir = os.path.dirname(project_dir)

cfg_file = os.path.basename(file_path)
cfg_file = os.path.join("extraction_result", cfg_file)

app = DCIRAnalysis(project_dir, cfg_file)
app.config_edb()
