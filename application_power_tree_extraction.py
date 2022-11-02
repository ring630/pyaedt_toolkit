import os.path
import tkinter as tk
from tkinter import filedialog

root = tk.Tk()
root.withdraw()

file_path = filedialog.askopenfilename()
project_dir = os.path.dirname(file_path)
cfg_file = os.path.basename(file_path)

from utils.power_tree_extraction import PowerTreeExtraction

app = PowerTreeExtraction(project_dir, cfg_file)
app.extract_power_tree(False)
