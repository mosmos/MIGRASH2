import time
import settings
import arcpy

if arcpy.Exists(settings.gdbpath):
      arcpy.Delete_management(settings.gdbpath)
      print("deleted old GDB")
else:
      print("no need to delete")

gdb = arcpy.CreateFileGDB_management(settings.datapath,settings.gdbname)
print(f"created new GDB:{gdb}")

for layer in settings.layers2:
      print (f"copying layer:{layer}")
      arcpy.FeatureClassToFeatureClass_conversion(settings.connectionpath+layer,settings.gdbpath,settings.layers2[layer])
      print(time.ctime())




