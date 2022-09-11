import time
import settings
import arcpy

# בודק אם קיים דאטה בייס ישן אם יש מוחק
if arcpy.Exists(settings.gdbpath):
      arcpy.Delete_management(settings.gdbpath)
      print("deleted old GDB")
else:
      print("no need to delete")

#מייצר דאטה בייס חדש
gdb = arcpy.CreateFileGDB_management(settings.datapath,settings.gdbname)
print(f"created new GDB:{gdb}")

# מכניס לתוך הדאטה בייס את כל השכבות שמעניינות אותנו כולל סינון ראשוני במידת הצורך
for layer in settings.layers2:
      print (f"copying layer:{layer}")
      try:
            results = arcpy.FeatureClassToFeatureClass_conversion(settings.connectionpath+layer,settings.gdbpath,settings.layers2[layer]["alias"],settings.layers2[layer]["sql"])
      except :
            print (results)      
      print(time.ctime())
                 
      

      







