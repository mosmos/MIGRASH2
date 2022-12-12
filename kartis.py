import time
print(time.ctime())
st = time.time()
import arcpy
import pandas
import settings
import exl_reader
import os

print("Hello {}!".format(settings.username))

   
# Checks if an old database exists. If there is, it will be deleted

if arcpy.Exists(settings.gdbpath):
      arcpy.Delete_management(settings.gdbpath)
      print("deleted old GDB")
else:
      print("No need to delete")
#Creates new GDB
gdb = arcpy.CreateFileGDB_management(settings.datapath,settings.gdbname)
print(f"created new GDB:{gdb}")

print("===================================================================================================================================")

#A loop that copies all layers from SDE to GDB
for layer in exl_reader.JsonOutput:
      print ("now copying {} -  Layer {} from {}".format(layer,list(exl_reader.JsonOutput).index(layer) + 1,len(exl_reader.JsonOutput)))
      items = exl_reader.JsonOutput.get(layer)

      if items["SQL"] == "None": #Conditional statement - converts Excel none value to Python's None
            items.update({'SQL': None})
      
      arcpy.FeatureClassToFeatureClass_conversion(settings.connectionpath+ items["PATH"],settings.gdbpath, layer ,items["SQL"])
      
print("===================================================================================================================================")

# Creates a 100 meter buffer for yeudei_karka layer
print ("creating buffer for yeudei_karka")
arcpy.Buffer_analysis(settings.gdbpath+"\yeudei_karka",settings.gdbpath+"\yeudei_karka_100m","100 meter")

print("===================================================================================================================================")

# Clip all layers with the buffer layer

for layer in exl_reader.JsonOutput:    
      print ("now cliping {} -  Layer {} from {}".format(layer,list(exl_reader.JsonOutput).index(layer) + 1,len(exl_reader.JsonOutput)))
      items = exl_reader.JsonOutput.get(layer)
      arcpy.Clip_analysis(settings.gdbpath+'\\'+ layer ,settings.gdbpath+"\yeudei_karka_100m",settings.gdbpath+'\\'+ layer + "_cliped")


print("===================================================================================================================================")


et = time.time()
res = et - st
final_res = str(res / 60)
print("Done!")
print("Good work {}! ".format(settings.username))
print("\N{smiling face with sunglasses}")
print(time.ctime())
print('Execution time:', final_res[0:final_res.find(".") + 3], 'minutes')
      

      