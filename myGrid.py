from pathlib import Path

import numpy as np
import openpyxl
from rich import print

from Sap2000py import Saproject

ProjectName = "myGrid"

# full path to the model
ModelPath = Path(".\Test\\" + ProjectName + ".sdb")

# Create a Sap2000py obj (default: attatch to instance and create if not exist)
Sap = Saproject()

# Change Sap api settings if you want
# Sap.createSap(AttachToInstance = True, SpecifyPath = False, ProgramPath = "your sap2000 path")

# Open Sap2000 program
Sap.openSap()

# Open Sap2000 sdb file (create if not exist, default: CurrentPath\\NewSapProj.sdb)
Sap.File.Open(ModelPath)
# And print the project information
#Sap.getProjectInfo()

# Can also creat a new blank model (or other models you need like 2DFrame / 3DFrame / etc.)
Sap.File.New_Blank()

# Get the model information (getSapVersion() will print and also returns the version)
vsesion = Sap.SapVersion
Sap.getSapVersion()

# Check your units (getUnits() will print and also returns the units)
unit = Sap.Units
Sap.getUnits()
# set Units as you wish (Just type in Sap.setUnits(""), it will show you the options in your IDE)
Sap.setUnits("KN_m_C")

# Add Materials
#Sap.Scripts.AddCommonMaterialSet(standard = "JTG")

# 
Sap.core.create_grid() # {"NumberBaysX" : 1, "NumberStorys" : 1}
#print("base_points : ", Sap.base_points)
#print("columns : ", Sap.columns)
#print("beams_x : ", Sap.beams_x)
#print("beams_y : ", Sap.beams_y)

#
Sap.RefreshView(0, False)

# Add elements to your group
#Sap.Scripts.Group.RemovefromGroup("base_points", Sap.base_points, "Point")
groups = [
    {"name": "base_points", "type": "Point"},
    {"name": "girders", "type": "Frame"},
    {"name": "crossbeams", "type": "Frame"}
]
for g in groups:
    #print("g: ", g['name'], g)
    Sap.Scripts.Group.AddtoGroup(g["name"], getattr(Sap, g["name"]), g["type"])
    items = Sap.Scripts.Group.GetElements(g["name"])
    #print(f'{g["name"]} : {items}')

# Select the group you need
#Sap.Scripts.Group.Select("base_points")

# Save file
Sap.File.Save(ModelPath)

# Remove all cases for analysis
#Sap.Scripts.Analyze.RemoveCases("All")
# Select cases for analysis
#Sap.Scripts.Analyze.AddCases(CaseName = ["DEAD", "MODAL", "G1k", "G2k", "Q1k", "H"])
# Delete Results
#Sap.Scripts.Analyze.DeleteResults("All")
# Run analysis
#Sap.Scripts.Analyze.RunAll()

# Save your file with a Filename(default: your ModelPath)
#Sap.File.Save()
Sap.File.Save(ModelPath)

# Don't forget to close the program
Sap.closeSap()