print("========== Step 1 ==========")

import time
from datetime import datetime
print(time.ctime())
st = time.time()
import arcpy
import pandas as pd
import settings
import exl_reader
import os

gdbpath="C:\DEV\GDATA"
connectionpath="C:\DEV\connectionfile\\sde01.sde\\"
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
            arcpy.AlterField_management(outputIntersect,"FID_{}".format(layer),None,"מספר יחודי בשכבה")
            arcpy.AlterField_management(outputIntersect,"FID_migrashim_humim",None,"חופף למגרש")
            
      
print("Step 2 completed successfully! :) ")

#=======================================================================================================================================
print("========== Step 3 ==========")  

IntersecList = [layer for layer in exl_reader.JsonOutput][1:]
migrashType = [arcpy.Describe(str(GDB) +'\\'+ layer + "Intersect").shapeType for layer in IntersecList]
migrashlist = []
migrashArealist = []
curser = arcpy.SearchCursor(migrashimpath) 
for row in curser:
      migrashlist.append(row.getValue("OBJECTID"))
      migrashArealist.append(row.getValue("Shape_Area"))
      del row
del curser 

with open("my_dataframe.html", "w",encoding="utf-8") as f:
      f.write(f"{settings.TopHTMLwithfilter}\n")
      for migrash in migrashlist[0:5]:
            title = "מגרש {}".format(migrash) 
            #link = '<a href="file:///C:/DEV/MIGRASH2/my_dataframe.html#{}"/a>'.format(migrash)  #הצג את {}</a>'.format(migrash,title)
            #f.write("<h1>{}</h1>".format(title) +"\n")
            f.write('<div id="מגרש-{}">'.format(migrash) + "\n")
            f.write('<h1>{}</h1>'.format(title))
            #f.write(link+"\n")
            print ("Now making report to migrash {} ".format(migrash))
            for layer in IntersecList:
                  items = exl_reader.JsonOutput.get(layer)
                  subtitle =  "שכבת {}:".format(items["HEB_NAME"])
                  Origfields = Convert(items["ATTRIBUTES"])
                  stayfields = ["FID_migrashim_humim","FID_{}".format(layer),"Shape_Length","Shape_Area"]
                  outputIntersect = str(GDB) +'\\'+ layer + "Intersect"
                  Fieldnames = [i.baseName for i in arcpy.ListFields(outputIntersect)]
                  Aliasnames = [i.aliasName for i in arcpy.ListFields(outputIntersect)]
                  removefields = [Aliasnames[Fieldnames.index(i)] for i in Fieldnames if i not in Origfields and i not in stayfields]
                  df = pd.DataFrame.from_records(data=arcpy.da.SearchCursor(outputIntersect,Fieldnames), columns=Aliasnames)
                  df.drop(columns = removefields,inplace= True)
                  #df = df.replace("NaN", "", regex=True)
                  rslt_df = df[df['חופף למגרש'] == migrash]
                  if len(rslt_df) > 0:
                        if items["TYPE"] == "Table" :
                              html_table =  rslt_df.to_html(index=False) 
                              # Add the title to the HTML table
                              html_with_subtitle = f'<h3  style="color:Green;">{subtitle} קיימת חפיפה של {len(rslt_df)} רשומות<h3>\n<h4>{html_table}<h4>'
                              f.write(html_with_subtitle + "\n")
                        elif items["TYPE"] == "YesNo" :
                              if migrashType[IntersecList.index(layer)] == "Polygon" :
                                    analyst = "אחוז השטח החופף - {}%".format(round(rslt_df.drop_duplicates(subset='Shape_Area')['Shape_Area'].sum()/migrashArealist[migrashlist.index(migrash)] *100,2))
                                    f.write(f'<h3  style="color:Green;">{subtitle} קיימת חפיפה של {len(rslt_df)} רשומות. {analyst}<h3>\n')
                              if migrashType[IntersecList.index(layer)] == "Polyline" :  
                                    analyst = f"אורך הקויים בתחום המגרש:{round(rslt_df.drop_duplicates(subset='Shape_Length')['Shape_Length'].sum(),2)} מטר"   
                                    f.write(f'<h3  style="color:Green;">{subtitle} קיימת חפיפה של {len(rslt_df)} רשומות. {analyst}<h3>\n')
                              if migrashType[IntersecList.index(layer)] == "Point" :  
                                    f.write(f'<h3  style="color:Green;">{subtitle} קיימת חפיפה של {len(rslt_df)} רשומות.<h3>\n')                      
                  else:
                       f.write('<h3  style="color:Red;">{} - לא קיימת חפיפה</h3>'.format(subtitle) + "\n") 
            f.write("<h1>-------------------------------<h1>" +"\n")
            f.write('</div>' + "\n")   
      f.write("<body>" + "\n")
      f.write("<html>" + "\n") 
                  

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
