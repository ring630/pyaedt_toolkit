# Introduction 
DCIR_Automation is intended to improve DCIR simulation workflow for complex PCB. This project is built on top of [PyAEDT](https://github.com/pyansys/PyAEDT). DCIR_Automation is licenced under the [MIT License](https://github.com/pyansys/PyAEDT/blob/main/LICENSE).

DCIR_Automation interacts directly with Electronics Database(EDB) which can be loaded into both SIwave and Ansys Electronics Desktop(AEDT).  Design data, in several industry-standard formats, can be converted into EDB format. Read AEDT Help for more information. [HFSS 3D Layout Help > Layout and Circuit Import Export Operations > Importing Layout Design Data](https://ansyshelp.ansys.com/account/secured?returnurl=/Views/Secured/Electronics/v212/en/home.htm%23../Subsystems/HFSS3DLayout/Content/3DLayout/ImportingLayoutDesignData.htm%3FTocPath%3DHFSS%25203D%2520Layout%7CHFSS%25203D%2520Layout%2520Help%7CLayout%2520and%2520Circuit%2520Import%2520Export%2520Operations%7CImporting%2520Layout%2520Design%2520Data%7C_____0)

The Ansys Electronics Desktop supports Extracta Import from Cadence. Note that Extracta.Exe is
a Cadence supplied executable and must be installed on your machine and on your executable
path for this to work.

# Getting Started
1. Unzip the package to local disk. Here the package will be zipped in C:\jupyter_folder. Now you should have two files as below

 - C:\Jupyter_folder\DCIR_Automation-0.1.1\app.ipynb. This is the jupyter notebook file.
 - C:\Jupyter_folder\DCIR_Automation-0.1.1\docs\environment.yml. This is the python config file which will be used in the next step.
 - C:\Jupyter_folder\DCIR_Automation-0.1.1\docs\jupyter_notebook_config.py. This file defines notebook working directory.
 - C:\Jupyter_folder\DCIR_Automation-0.1.1\docs\Jupyter Notebook (dcir_automation).Ink. This is a shortcut to launch notebook.

3. Install Python3 and create a virtual environment-
 - Download and install Anaconda3. https://www.anaconda.com/products/individual.
 - Open anaconda prompt Start -> Anaconda3 -> Anaconda Prompt(Anaconda3). Execute below code. A virtual environment named dcir_automation will be created.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
conda env create -f C:\Jupyter_folder\DCIR_Automation-0.1.1\docs\environment.yml
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
5. Copy jupyter_notebook_config.py into C:\Users\[SIGNUM]\.jupyter
8. Double click Jupyter Notebook (dcir_automation).Ink to launch Jupyter notebook.
