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
from collections import Counter

gdbpath="C:\DEV\GDATA"
connectionpath="C:\DEV\connectionfile\\dgt-sde01db720.sde\\"
excelpath="C:\DEV\MIGRASH2\MIGRASH_MILON.xlsx"
username = os.getlogin()

print("Hello {}!".format(username))
   
#Creates a new file GDB file with time and date
gdbname="{}_LAYERSFORPROCESS.gdb".format(datetime.now().strftime("%Y%m%d%H%M"))

GDB = arcpy.CreateFileGDB_management(gdbpath,gdbname)

print("created new GDB:", GDB)
print("Step 1 completed successfully! :) ")

#=======================================================================================================================================
print("========== Step 2 ==========")
def Convert(string):
    li = list(string.split(","))
    return li

for layer in exl_reader.JsonOutput:
      print ("Now copying {} -  Layer {} from {}".format(layer,list(exl_reader.JsonOutput).index(layer) + 1,len(exl_reader.JsonOutput)))
      items = exl_reader.JsonOutput.get(layer)
      if items["SQL"] == "None" : #Conditional statement - converts Excel none value to Python's None
            items.update({'SQL': None})    
      layerpath = connectionpath + items["PATH"]  
      arcpy.FeatureClassToFeatureClass_conversion(layerpath, GDB, layer ,items["SQL"])
      outputLayer = str(GDB) + "\\" + layer
      Fieldnames = arcpy.ListFields(outputLayer)
      stayfields = ["Shape","OBJECTID","Shape_Length","Shape_Area"]
      Origfields = Convert(items["ATTRIBUTES"])
      for i in Fieldnames:
            if i.baseName not in stayfields and i.baseName not in Origfields :
                  arcpy.DeleteField_management(outputLayer, i.baseName)
      if layer == "migrashim_humim":
            migrashimpath = str(GDB) + '\\' + layer
      else:
            outputIntersect = str(GDB) +'\\'+ layer + "Intersect"
            print ("Now making Intersect of layer {} with migrashim_humim layer".format(layer))
            arcpy.Intersect_analysis((outputLayer,migrashimpath),outputIntersect,"ALL", None, "INPUT")
      
print("Step 2 completed successfully! :) ")

#=======================================================================================================================================
print("========== Step 3 ==========")  

IntersecList = [layer for layer in exl_reader.JsonOutput][1:]
migrashlist = []
curser = arcpy.SearchCursor(migrashimpath)
for row in curser:
      migrashlist.append(row.getValue("OBJECTID"))
      del row
del curser 


result = result = {m: set(IntersecList) for m in migrashlist}


result = {}
for migrash in migrashlist:
      print ("Now making report to migrash {} ".format(migrash))
      resultlayer = {}
      for layer in IntersecList:
            items = exl_reader.JsonOutput.get(layer)
            Origfields = Convert(items["ATTRIBUTES"])
            outputIntersect = str(GDB) +'\\'+ layer + "Intersect"
            Fieldnames = [i.baseName for i in arcpy.ListFields(outputIntersect)]
            curser = arcpy.SearchCursor(outputIntersect) 
            records = []     
            for row in curser:
                  FID_migrashim_humim = row.getValue("FID_migrashim_humim")
                  if FID_migrashim_humim == migrash:
                        record = []
                        for field in Fieldnames:
                              if field in Origfields or field == "FID_migrashim_humim":
                                    record.append({field:row.getValue(field)})
                        records.append(record)      
                        resultlayer.update({layer:records})
      result.update({migrash:resultlayer})
      
                              
f = open("report.txt", "a")
f.write(str(result))
f.close()
 
                              
print("Step 3 completed successfully!")
#=======================================================================================================================================
print("========== Step 4 ==========")

et = time.time()
res = et - st
final_res = str(res / 60)
print("Done!")
print("Good work {}! ".format(settings.username))
print("\N{smiling face with sunglasses}")
print(time.ctime())
print('Execution time:', final_res[0:final_res.find(".") + 3], 'minutes')
    
                                          
