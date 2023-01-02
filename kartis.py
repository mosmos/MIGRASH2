print("========== Step 1 ==========")

import time
from datetime import datetime
print(time.ctime())
st = time.time()
import arcpy
import pandas
import settings
import exl_reader
import os

print("Hello {}!".format(settings.username))
   
#Creates a new file GDB file with time and date
gdbname="{}_LAYERSFORPROCESS.gdb".format(datetime.now().strftime("%Y%m%d%H%M"))

GDB = arcpy.CreateFileGDB_management(settings.gdbpath,gdbname)

print("created new GDB:", GDB)
print("Step 1 completed successfully! :) ")

#=======================================================================================================================================
print("========== Step 2 ==========")
#Copies all layers from SDE to GDB and make the join layer for the next steps. 
##Create join layer for step 4

for layer in exl_reader.JsonOutput:
      print ("Now copying {} -  Layer {} from {}".format(layer,list(exl_reader.JsonOutput).index(layer) + 1,len(exl_reader.JsonOutput)))
      items = exl_reader.JsonOutput.get(layer)
      if items["SQL"] == "None" : #Conditional statement - converts Excel none value to Python's None
            items.update({'SQL': None})      
      arcpy.FeatureClassToFeatureClass_conversion(settings.connectionpath+ items["PATH"], GDB, layer ,items["SQL"])
      #Create join layer for the next step
      if layer == "migrashim_humim":
            print("Now making the join layer")
            arcpy.FeatureClassToFeatureClass_conversion(settings.connectionpath+ items["PATH"], GDB, layer + "_For_Join" ,items["SQL"])
            Join_Layer_Path = str(GDB) + "\\" + layer + "_For_Join"
            Fieldnames = arcpy.ListFields(Join_Layer_Path)
            stayfields = ["Shape","OBJECTID","Shape_Length","Shape_Area"]
            for i in Fieldnames:
                  if i.baseName not in stayfields:
                        arcpy.DeleteField_management(Join_Layer_Path, i.baseName)

print("Step 2 completed successfully!")

#=======================================================================================================================================
print("========== Step 3 ==========")
#Adds to "migrashim_humim" layer information about overlap or buffer with each layer.

layerlist = []
for layer in exl_reader.JsonOutput:
      if layer != "migrashim_humim":
            items = exl_reader.JsonOutput.get(layer)
            layerName = items["HEB_NAME"]
            codeblockLayer = """def Layername():
                  return "{}" """.format(layerName)   #function for field "Layer_Name"


            codeblockwithin = """def within(x): 
                  if x == 0:
                        return "Yes"
                  else:
                        return "No" """ #function for field "within"
                      
            codeblockBuffer = """def buffer(x):
                  if x > 0:
                        return "Yes"
                  else:
                        return "No" """ #function for field "buffer"
                      
            print ("Now making a spatial join to  {} -  Layer {} from {}".format(layer,list(exl_reader.JsonOutput).index(layer) + 1,len(exl_reader.JsonOutput)))
            Join_Layer_Path = str(GDB) +'\\' "migrashim_humim_" + "Join_" + layer
            arcpy.SpatialJoin_analysis(str(GDB) +'\\'+ 'migrashim_humim_For_Join',str(GDB) +'\\'+ layer, Join_Layer_Path,"JOIN_ONE_TO_MANY", "KEEP_ALL",None,"CLOSEST", "{} Meters".format(items["BUFFER"]), "Distance")
            arcpy.CalculateField_management(Join_Layer_Path,'Layer_Name', "Layername()", "PYTHON3",codeblockLayer, "TEXT", "NO_ENFORCE_DOMAINS")    
            arcpy.CalculateField_management(Join_Layer_Path,'within',"within(!Distance!)","PYTHON3",codeblockwithin,"TEXT", "NO_ENFORCE_DOMAINS")
            arcpy.CalculateField_management(Join_Layer_Path,'buffer',"buffer(!Distance!)","PYTHON3",codeblockBuffer,"TEXT", "NO_ENFORCE_DOMAINS")      
              
            Fieldnames = arcpy.ListFields(Join_Layer_Path)           
            stayfields = ["Shape","OBJECTID","Shape_Length","Shape_Area","within","buffer","Layer_Name","JOIN_FID","TARGET_FID"]
            for i in Fieldnames:
                  if i.baseName not in stayfields:
                        arcpy.DeleteField_management(Join_Layer_Path, i.baseName) #Deleting all unnecessary fields

            layerlist.append(Join_Layer_Path)
            
arcpy.Merge_management(layerlist,str(GDB) +'\\'+ "merge")  #Combines all layers to create one table

#Sorts the table by the unique field of "migrashim_humim"
arcpy.Sort_management(str(GDB) +'\\'+ "merge",str(GDB) +'\\'+ "migrashim_humim_all","TARGET_FID ASCENDING;Layer_Name ASCENDING", "UR")

#Editing the final table
arcpy.AlterField_management(str(GDB) +'\\'+ "migrashim_humim_all", "TARGET_FID", '', "ערך FID בשכבת מגרשים חומים")
arcpy.AlterField_management(str(GDB) +'\\'+ "migrashim_humim_all", "JOIN_FID", '', "ערך בשכבת המקור")
arcpy.DeleteField_management(str(GDB) +'\\'+ "migrashim_humim_all","ORIG_FID", "DELETE_FIELDS")

print("Step 3 completed successfully!")
#=======================================================================================================================================
print("========== Step 4 ==========")
#Combines the layers to "migrashim_humim" layer by Spatial join and measures whether there is an overlap or closeness of up to 100 meters from the layer by "Distance" column.

for layer in exl_reader.JsonOutput:
      if layer != "migrashim_humim":
            items = exl_reader.JsonOutput.get(layer)
            print ("Now making a spatial join to  {} -  Layer {} from {}".format(layer,list(exl_reader.JsonOutput).index(layer) + 1,len(exl_reader.JsonOutput)))
            Layer_Join_Path = str(GDB) +'\\'+ layer + "_join"
            arcpy.SpatialJoin_analysis(str(GDB) +'\\'+ layer, str(GDB) +"\migrashim_humim_For_Join",Layer_Join_Path,"JOIN_ONE_TO_MANY", "KEEP_ALL",None,"CLOSEST", "{} Meters".format(items["BUFFER"]), "Distance")
            #arcpy.CalculateField_management(str(GDB) +'\\'+ layer + "_jointo",'Layer_Name', "Layername()", "PYTHON3",codeblockLayer, "TEXT", "NO_ENFORCE_DOMAINS")    
            arcpy.CalculateField_management(Layer_Join_Path ,'within',"within(!Distance!)","PYTHON3",codeblockwithin,"TEXT", "NO_ENFORCE_DOMAINS")
            arcpy.CalculateField_management(Layer_Join_Path ,'buffer',"buffer(!Distance!)","PYTHON3",codeblockBuffer,"TEXT", "NO_ENFORCE_DOMAINS") 
            Fieldnames = arcpy.ListFields(Layer_Join_Path) 
            stayfields = settings.Convert(items["ATTRIBUTES"])
            for i in Fieldnames:
                  if i.baseName not in stayfields and i.baseName != ("Shape","OBJECTID","Shape_Length","Shape_Area"):
                        arcpy.DeleteField_management(Layer_Join_Path, i.baseName) #Deleting all unnecessary fields
                 
      

print("Step 4 completed successfully!")
#=======================================================================================================================================
print("========== Step 5 ==========")

et = time.time()
res = et - st
final_res = str(res / 60)
print("Done!")
print("Good work {}! ".format(settings.username))
print("\N{smiling face with sunglasses}")
print(time.ctime())
print('Execution time:', final_res[0:final_res.find(".") + 3], 'minutes')

