import time
import settings
print(time.ctime())

import arcpy

geodataexist=arcpy.Exists(settings.gdbpath)

if geodataexist == True:
      arcpy.Delete_management(settings.gdbpath)
      print("deleted old GDB")
else:
      print("no need to delete")

arcpy.CreateFileGDB_management(settings.datapath,settings.gdbname)
print("created new GDB")

for i in range(len(settings.layers)):
      print (settings.layers[i])
      arcpy.FeatureClassToFeatureClass_conversion(settings.connectionpath+settings.layers[i],settings.gdbpath,settings.layersnickname[i])
      

print(time.ctime())




