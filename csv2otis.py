# -*- coding: utf-8 -*-
"""
Created on Thu Aug 24 09:41:38 2023

@author: 223057234

simple python script to convert .csv files into otis format
"""

#Adding a simple note to test github

from tkinter import filedialog as fd # Handles actually calling the windows file dialog for selecting files and folders
from tkinter import Button, Variable, Listbox, Tk, EXTENDED, BOTH # Different components I use for the GUI
from os import chdir # Lets you make calls to windows just like a command prompt
from os.path import basename
from os.path import realpath # Gets the full path of a file
from os.path import dirname # Gets the directory name from a path
from os.path import splitext
from pandas import DataFrame # Lets the user create a Dataframe
from pandas import concat
from pandas import read_csv

#%%

# =============================================================================
# Function to open a GUI that lets user select a file/files that contain the data otis will turn into a map
# =============================================================================

def load_data():
    '''
    Simple script to grab the file address from a file or files that a user selects

    Returns
    -------
    datafile : list
        the full path of the datafiles the user selects.

    '''
    root = Tk() # Open an instance of windows GUI manager called root
    filetypes = ( # only allow the following file types to be seen
        ('csv files', '*.csv'),
        ('text files', '*.txt'),
        ('cbaero data files', '*.dat'),
        ('All files', '*.*')
    )
    #store the read files in the IR_Images list
    datafiles = fd.askopenfilenames(title="Please select the settings file for this experiment",filetypes=filetypes)
    root.destroy() # Close the instance of windows GUI manager
    
    dir_path = "" # Create a variable that holds an empty string. This will become the write directory
    dir_path = dirname(realpath(datafiles[0])) # Assuming you want to be working in the same directory as the files you just opened. Take the directory from the first file you opened
    chdir(dir_path) # Take the dir_path string and use the operating system to change pythons working directory to whatever was selected
    
    print("Data Files Selected:")
    for each in datafiles:
        print(each)
    print("Write Path for Output: ",dir_path)
    
    return datafiles
    
datafiles = load_data() # call the previously defined load_settings() function to collect the addresses of the user selected data files

#%%

# =============================================================================
# Combine all selected datafiles for making the output
# =============================================================================

def Open_Data(datafiles):
    
    data = DataFrame() # Create a new pandas Dataframe where the data will be stored
    
    if splitext(datafiles[-1])[-1]=='.dat':
        print("parsing cbaero .dat file")
        with open(datafiles[-1], 'r') as file:
            contents = file.readlines()
            for line in contents:
                if line.find("Function Data:")!=-1:
                    starting_line = contents.index(line)    
        data = read_csv(datafiles[-1], dtype='str', skiprows=starting_line+1, delim_whitespace=True, skip_blank_lines=True)
        
    if splitext(datafiles[-1])[-1] in ['.csv','.txt']:
        print("parsing file assuming csv format")
        for i in range(0,len(datafiles)): # For each of the files selected previously
            data = concat([data,read_csv(datafiles[i],dtype='str')],ignore_index=True) # Now read the data into the dataframe.
    
    return data # return a panda's dataframe with all the available data combined

data = Open_Data(datafiles) # output the data into a dataframe called "data"

#%%

# =============================================================================
# Create OTIS map from dataframe
# =============================================================================

def Create_OTIS_ITD(data, independant_columns = [""], dependant_columns = [""], scale_factor = "1.0", Title = "You can add a title here"):
    
    variable_formatting = []
    for each in independant_columns:
        variable_formatting.append(len(data[each].unique()))
    
    OTIS = []
    OTIS.append("! {}".format(Title))
    
    for deps in dependant_columns:
        OTIS.append("\n! Table Name for the tab() function\n")
        OTIS.append("{}\n".format(deps))
        OTIS.append("! ABLOCK variable name that this table contains\n")
        OTIS.append("{}\n".format(deps))   
    
        OTIS.append("! scale factor\n")
        OTIS.append("{}\n".format(scale_factor))
        OTIS.append("! number of direct variable multipliers (typically 1)\n")
        OTIS.append("1\n")
        OTIS.append("! NCOEF (Number of Dependant Coefficients)\n")
        OTIS.append("NCOEF {}\n".format(len(dependant_columns)))
        OTIS.append("! Number of Independant Coefficients:\n")
        OTIS.append("{}\n".format(len(independant_columns)))
            
        for each in independant_columns:
            OTIS.append("! Independant Variable Name:\n")
            OTIS.append("{}\n".format(each))
            OTIS.append("! Linear interpolation on {}\n".format(each))
            OTIS.append("! Number of unique values for {}:\n".format(each))
            OTIS.append(str(len(data[each].unique())))
            OTIS.append("\n")
            OTIS.append(' '.join(data[each].unique()))
            OTIS.append("\n")
        # OTIS.append("!\n")

        increments = []
        if len(variable_formatting) > 1:
            for each in reversed(variable_formatting[1:]):
                if increments ==[]:
                    increments.append(each)
                else:
                    increments.append(each*increments[-1])
        else:
            increments = [variable_formatting[0]]
        
        prod = 1
        for each in variable_formatting:
            prod = prod*each
        
        i = 0
        while i<prod:
            if len(variable_formatting)>=1 and i==0:
                OTIS.append("! Dependant Variable {}\n".format(dependant_columns[0]))
             
            for index, x in enumerate(increments):
                if int(i%x) == 0:
                    if index == 0 and i>0:
                        OTIS.append("\n")
                    if index >= 1:
                        # print(index, x, i, int((i/x)%len(data[independant_columns[-2-1]].unique())))
                        # print("! Independant Variable {} = {}\n".format(independant_columns[-2-index],data[independant_columns[-2-index]].unique()[int((i/x)%len(data[independant_columns[-2-1]].unique()))]))
                        OTIS.append("! Independant Variable {} = {}\n".format(independant_columns[-2-index],data[independant_columns[-2-index]].unique()[int((i/x)%len(data[independant_columns[-2-1]].unique()))]))
                        
            OTIS.append("{:>10} ".format(data[dependant_columns].iat[i,0]))
            i+=1

    OTIS.append("\n!")
    
    OTIS_Output = open("OTIS_"+basename(datafiles[0])+".ITD",'w')
    OTIS_Output.writelines(OTIS)
    OTIS_Output.close()
    return OTIS

#%%

# =============================================================================
# A function that opens a GUI window, reads the columns from a pandas database, and lets the user select columns
# =============================================================================

def Selection_GUI(data, title):
    window = Tk()
    window.title(title)
    window.geometry('500x300')
    
    selection = []
    
    def print_selection():
        print("selection:")
        for each in listbox.curselection():
            selection.append(data.keys().to_list()[each])
            print(data.keys().to_list()[each])
        window.quit()
        
    b1 = Button(window, text='Select', width=15, height=2, command=print_selection)
    b1.pack()
    
    var = Variable(value=data.keys().to_list())
    listbox = Listbox(window,listvariable=var,height=6,selectmode=EXTENDED)
    listbox.pack(expand=True, fill=BOTH)
    
    window.mainloop()
    window.destroy()
    
    return selection

#%%
if splitext(datafiles[-1])[-1]=='.dat':
    print("Converting CBAero data to OTIS Format")
 
    if {"X_1","X_2","X_3","F"}.issubset(data.columns) and not {"X_4"}.issubset(data.columns):
        data['MACH']=data['X_1']
        data['Q']=data['X_2']
        data['ALPHAD']=data['X_3']
        data[basename(datafiles[0]).split(".")[1]]=data['F']
        ind_col=["MACH","Q","ALPHAD"]
        dep_col=[basename(datafiles[0]).split(".")[1]]
    
    elif {"X_1","X_2","X_3","F"}.issubset(data.columns) and {"X_4"}.issubset(data.columns):
        data['MACH']=data['X_1']
        data['Q']=data['X_2']
        data['ALPHAD']=data['X_3']
        data['FlapAngle']=data['X_4']
        data[basename(datafiles[0]).split(".")[1]]=data['F']
        ind_col=["MACH","Q","ALPHAD","FlapAngle"]
        dep_col=[basename(datafiles[0]).split(".")[1]]
    
if splitext(datafiles[-1])[-1] in ['.csv','.txt']:
    print("Processing csv or txt file")
    
    if {'X10','X11','X12','AoA','Mdot[lbm/s]','Thrust[lbf]'}.issubset(data.columns):
        print("1DE Engine Detected")
        data.replace('-','0',inplace=True)
        data['ALT']=data['X10']
        data['MACH']=data['X11']
        data['XPAR(1)']=data['X12']
        data['ALPHAD']=data['AoA']
        data['THRUST']=data['Thrust[lbf]']
        data['NISP']=(data['Thrust[lbf]'].astype(float)/data['Mdot[lbm/s]'].astype(float))
        data.fillna(0,inplace=True)
        
        ind_col = ['ALT','MACH','XPAR(1)','ALPHAD']
        dep_col = ['THRUST','NISP']

    else:
        print("user input required")
        
        print("Please type up to 5 independant variables from the GUI")    
        ind_col = Selection_GUI(data, title = "Independant Variable Selection")
        
        print("Please a dependant variable from the GUI")
        dep_col = Selection_GUI(data, title = "Dependant Variable Selection")
        
#%%
print("creating output in OTIS format")
Create_OTIS_ITD(data, independant_columns = ind_col, dependant_columns = dep_col)
print("Conversion Complete")
