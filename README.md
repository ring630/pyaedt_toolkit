# Introduction 
DCIR_Automation is intended to setup DCIR simulation for complex PCB. This project is built on top of PyAEDT https://github.com/pyansys/PyAEDT. DCIR_Automation is licenced under the `MIT License

<https://github.com/pyansys/PyAEDT/blob/main/LICENSE>`_.
DCIR_Automation interacts directly with Ansys Electronics Database(AEDB) which can be loaded into both SIwave and Ansys Electronics Desktop(AEDT).
DCIR_Automation extends existing DCIR workflow functionalities as below.

1, extract power trees from EDB by user provided voltage regulator module(VRM) reference designator(Refdes) together with VRM output net name or output inductor Refdes.

2, list all sink components on power tree per VRM.

3, assign current to sink components from user defined local library.  

# 
    Cadence dependency
# Getting Started
1. download and install Anaconda3. https://www.anaconda.com/products/individual
2. open anaconda prompt to create a virtual environment dcir_automatio and install PyAEDT

    conda create —-name dcir_automation python= 3.8 pandas numpy matplotlib ipython   #create a virtual environment
    
    conda info --envs                                         #list all environments
    
    conda activate dcir_automation                            #activate the new environement
   
    pip install pyvista                                       #install pyvista
    
    pip install pyaedt                                        #install PyAEDT
3. Download dcir_automation code and unzip it to local disk. For example C:\DCIR_Automation

# Prepare user defined input files
