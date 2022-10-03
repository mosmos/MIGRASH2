import time
print(time.ctime())
import arcpy
import pandas
import settings

   
# בודק אם קיים דאטה בייס ישן אם יש מוחק
if arcpy.Exists(settings.gdbpath):
      arcpy.Delete_management(settings.gdbpath)
      print("deleted old GDB")
else:
      print("no need to delete")

#מייצר דאטה בייס חדש
gdb = arcpy.CreateFileGDB_management(settings.datapath,settings.gdbname)
print(f"created new GDB:{gdb}")

#מייצר מתוך האקסל רשימה של שכבות עם המאפיינים הנוספים של כל שכבה
layerslist_excel = pandas.read_excel(settings.excelpath, sheet_name='layers')
layerslist_dict = layerslist_excel.to_dict(orient='records')

# משנה את הערך הריק (נון) של האקסל בערך הריק (נון) של פיטון הכרחי כי אחרת הוא לא נקרא בפונקציה של העתקת השכבות של הארק פיי
for layer in layerslist_dict:

      if (layerslist_dict[settings.counterone]["SQL"] == "None") is True:
            layerslist_dict[settings.counterone]["SQL"]=None
            settings.counterone+=1
      else:
            print("no need to change value")
            settings.counterone+=1

         
# מכניס בלופ לתוך הדאטה בייס החדש שייצרנו את כל השכבות שהוזנו באקסל 
for layer in layerslist_dict:
      
      print (f"now copying {layer}")
      arcpy.FeatureClassToFeatureClass_conversion(settings.connectionpath+layerslist_dict[settings.countertwo]["PATH"],settings.gdbpath,layerslist_dict[settings.countertwo]["ALIAS"],layerslist_dict[settings.countertwo]["SQL"])
      settings.countertwo+=1


# מייצר באפר של 100 מטר לשכבת המגרשים
print ("creating buffer for yeudei_karka")
arcpy.Buffer_analysis(settings.gdbpath+"\yeudei_karka",settings.gdbpath+"\yeudei_karka_100m","100 meter")


# חותך את כלל השכבות עלפי שכבת היעודי קרקע עם הבאפר

for layer in layerslist_dict:
      
      print (f"cliping {layer}")
      arcpy.Clip_analysis(settings.gdbpath+'\\'+layerslist_dict[settings.counterthree]["ALIAS"],settings.gdbpath+"\yeudei_karka_100m",settings.gdbpath+'\\'+layerslist_dict[settings.counterthree]["ALIAS"]+"_cliped")
      settings.counterthree+=1




print(time.ctime())

      

      












# for layer in settings.layers2:
#       print (f"copying layer:{layer}")
#       try:
#             results = arcpy.FeatureClassToFeatureClass_conversion(settings.connectionpath+layer,settings.gdbpath,settings.layers2[layer]["alias"],settings.layers2[layer]["sql"])
#       except :
#             print (results)      
#       print(time.ctime())