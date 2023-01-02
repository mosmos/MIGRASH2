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

#Checks if an old database exists. If there is, it will be deleted
gdbname="{}_LAYERSFORPROCESS.gdb".format(datetime.now().strftime("%Y%m%d%H%M"))

GDB = arcpy.CreateFileGDB_management(settings.gdbpath,gdbname)

print("created new GDB:", GDB)
print("Step 1 completed successfully! :) ")

#=======================================================================================================================================
print("========== Step 2 ==========")
#Copies all layers from SDE to GDB

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
#Combines the layers to "yeudei_karka" layer by Spatial join and measures whether there is an overlap or closeness of up to 100 meters from the layer by "Distance" column.

for layer in exl_reader.JsonOutput:
      if layer != "migrashim_humim":
            items = exl_reader.JsonOutput.get(layer)
            print ("Now making a spatial join to  {} -  Layer {} from {}".format(layer,list(exl_reader.JsonOutput).index(layer) + 1,len(exl_reader.JsonOutput)))
            arcpy.SpatialJoin_analysis(str(GDB) +'\\'+ layer, str(GDB) +"\migrashim_humim_For_Join",str(GDB) +'\\'+ layer + "_join","JOIN_ONE_TO_MANY", "KEEP_ALL",None,"CLOSEST", "{} Meters".format(items["BUFFER"]), "Distance")
            print(items["BUFFER"])
      

print("Step 3 completed successfully!")

print("========== Step 4 ==========")
#Creates a new layer that shows only the values whose distance is between 0 - 100 by Select
for layer in exl_reader.JsonOutput:
      if layer != "migrashim_humim":
            print ("now filtering {} -  Layer {} from {}".format(layer,list(exl_reader.JsonOutput).index(layer) + 1,len(exl_reader.JsonOutput)))
            arcpy.analysis.Select(str(GDB) +'\\'+ layer + "_join", str(GDB) +'\\'+ layer + "_Select", "Distance <> -1")

print("Step 4 completed successfully!")

print("========== Step 5 ==========")
#read the cursor fields from the config file and write to report.txt
with open("Report.csv","w") as Report: #Create report file
      for layer in exl_reader.JsonOutput:
            if layer != "migrashim_humim":
                  print ("Now making a report to {} -  Layer {} from {}".format(layer,list(exl_reader.JsonOutput).index(layer) + 1,len(exl_reader.JsonOutput)))
                  items = exl_reader.JsonOutput.get(layer)
                  layer_fields = arcpy.ListFields(str(GDB) +'\\'+ layer + "_Select")
                  layer_fields = [i.name for i in layer_fields]
                  layer_fields = settings.Convert(items["ATTRIBUTES"])

                  with arcpy.da.SearchCursor(str(GDB) +'\\'+ layer + "_Select", layer_fields) as cur:
                        #print(layer_fields)
                        Report.write("\nLayer {} - {}".format(list(exl_reader.JsonOutput).index(layer) + 1,layer))
                        Report.write("\n" + str(layer_fields))
                        for row in cur:
                              str_row = str(row)
                              Report.write("\n" + str_row[1:-1])
                              #Report.write("\n==================================================")


print("========== Step 6 ==========")

et = time.time()
res = et - st
final_res = str(res / 60)
print("Done!")
print("Good work {}! ".format(settings.username))
print("\N{smiling face with sunglasses}")
print(time.ctime())
print('Execution time:', final_res[0:final_res.find(".") + 3], 'minutes')












#A loop that: 
# Step 1 -copies all layers from SDE to GDB
# Step 2 -  Combines the layers to "yeudei_karka" layer by Spatial join and measures whether there is an overlap or closeness of up to 100 meters from the layer by "Distance" column.
# Step 3 - Creates a new layer that shows only the values whose distance is between 0 - 100 by Select
# Step 4 - read the cursor fields from the config file and write to report.txt



with open("Report.csv","w") as Report: #Create report file
      for layer in exl_reader.JsonOutput:
      #Step 1 -copies all layers from SDE to GDB
            print ("Now copying {} -  Layer {} from {}".format(layer,list(exl_reader.JsonOutput).index(layer) + 1,len(exl_reader.JsonOutput)))
            items = exl_reader.JsonOutput.get(layer)

            if items["SQL"] == "None" : #Conditional statement - converts Excel none value to Python's None
                  items.update({'SQL': None})
            
            arcpy.FeatureClassToFeatureClass_conversion(settings.connectionpath+ items["PATH"],settings.gdbpath, layer ,items["SQL"])

            Fields = settings.Convert(items["ATTRIBUTES"])

            print(Fields)

      #Step 2 -  Combines the layers to "yeudei_karka" layer by Spatial join and measures whether there is an overlap or closeness of up to 100 meters from the layer by "Distance" column.
            if layer == "migrashim_humim":
                  yeudei_karka_fields = arcpy.ListFields(settings.gdbpath+'\\'+ layer)
                  yeudei_karka_fields = [i.name for i in yeudei_karka_fields]

            else:

                  print ("Now making a spatial join to  {} -  Layer {} from {}".format(layer,list(exl_reader.JsonOutput).index(layer) + 1,len(exl_reader.JsonOutput)))
                  arcpy.SpatialJoin_analysis(settings.gdbpath+'\\'+ layer,settings.gdbpath+"\migrashim_humim",settings.gdbpath+'\\'+ layer + "_join","JOIN_ONE_TO_MANY", "KEEP_ALL",None,"CLOSEST", "100 Meters", "Distance")
      
      # Step 3 - Creates a new layer that shows only the values whose distance is between 0 - 100 by Select
      #            
                  print ("now filtering {} -  Layer {} from {}".format(layer,list(exl_reader.JsonOutput).index(layer) + 1,len(exl_reader.JsonOutput)))
                  arcpy.analysis.Select(settings.gdbpath+'\\'+ layer + "_join", settings.gdbpath+'\\'+ layer + "_Select", "Distance <> -1")
                  
      # Step 4 - read the cursor fields from the config file and write to report.txt
                  print ("Now making a report to {} -  Layer {} from {}".format(layer,list(exl_reader.JsonOutput).index(layer) + 1,len(exl_reader.JsonOutput)))
                  layer_fields = arcpy.ListFields(settings.gdbpath+'\\'+ layer + "_Select")
                  layer_fields = [i.name for i in layer_fields]

                  with arcpy.da.SearchCursor(settings.gdbpath+'\\'+ layer + "_Select", Fields) as cur:
                        #print(layer_fields)
                        Report.write("\nLayer {} - {}".format(list(exl_reader.JsonOutput).index(layer) + 1,layer))
                        Report.write("\n" + str(Fields))
                        for row in cur:
                              #print(row)
                              Report.write("\n" + str(row))
                        Report.write("\n==================================================")

print("===================================================================================================================================")


et = time.time()
res = et - st
final_res = str(res / 60)
print("Done!")
print("Good work {}! ".format(settings.username))
print("\N{smiling face with sunglasses}")
print(time.ctime())
print('Execution time:', final_res[0:final_res.find(".") + 3], 'minutes')
      

      