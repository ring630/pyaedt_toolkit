# Introduction 
The purpose of the project is to automate DCIR analysis worflow. Power tree and its associated components are extracted based on user provided VRM refdes and its output net name. The extraction searches components through serial inductors.

# Getting Started
1. download and install Anaconda3. https://www.anaconda.com/products/individual
2. open anaconda prompt to create a virtual environment dcir_automatio and install PyAEDT

    conda create —-name dcir_automation python= 3.8 pandas numpy matplotlib    #create a virtual environment
    
    conda info --envs                                         #list all environments
    
    conda activate dcir_automation                            #activate the new environement
   
    pip install pyaedt                                        #install PyAEDT
3. Download dcir_automation code and unzip it to local disk. For example C:\Users\hzhou\OneDrive - ANSYS, Inc\PyCharm_project\DCIR_Automation-main
4. download and install pycharm. https://www.jetbrains.com/pycharm/download/#section=windows
    
    Create a new pycharm project from existing code
    ![image](https://user-images.githubusercontent.com/27995305/131300279-5222f5a2-1804-49e5-9121-5fe345ab2b8b.png)


# Analyze the example project
![image](https://user-images.githubusercontent.com/27995305/131300123-67fbee98-0ac5-47c5-b77f-f535a4e687f2.png)


