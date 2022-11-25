import os.path
import tkinter as tk
from tkinter import filedialog

root = tk.Tk()
root.withdraw()

file_path = filedialog.askopenfilename()
project_dir = os.path.dirname(file_path)
cfg_file = os.path.basename(file_path)

from dcir_power_tree import PowerTreeExtraction

app = PowerTreeExtraction(project_dir, cfg_file)
app.extract_power_tree(aedt_nexxim=True, pdf_figsize=(48, 24))
