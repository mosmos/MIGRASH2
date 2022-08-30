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

for layer in settings.layers2:
      print (layer)
      arcpy.FeatureClassToFeatureClass_conversion(\
            settings.connectionpath+layer,\
            settings.gdbpath,\
            settings.layers2[layer])
      

print(time.ctime())




