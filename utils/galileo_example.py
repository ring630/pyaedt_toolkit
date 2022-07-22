import os
import tempfile
import shutil
from pyaedt import generate_unique_name, examples

###############################################################################
# Download file
# ~~~~~~~~~~~~~
# Download the AEDB file and copy it in the temporary folder.

def get_galileo_exmaple_board():
    tmpfold = tempfile.gettempdir()
    temp_folder = os.path.join(tmpfold, generate_unique_name("Example"))
    if not os.path.exists(temp_folder):
        os.makedirs(temp_folder)
    example_path = examples.download_aedb()
    targetfolder = os.path.join(temp_folder, "Galileo.aedb")
    if os.path.exists(targetfolder):
        shutil.rmtree(targetfolder)
    shutil.copytree(example_path[:-8], targetfolder)
    targetfile = os.path.join(targetfolder)
    return targetfile

