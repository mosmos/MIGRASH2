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
import shutil

#Defines the code and project path 
gdbpath="C:\DEV\GDATA"
connectionpath="C:\DEV\connectionfile\\sde01.sde\\"
excelpath="C:\DEV\MIGRASH2\MIGRASH_MILON.xlsx"
username = os.getlogin()

print("Hello {}!".format(username))

# Define project location
currentDirectory = os.getcwd()
   
#Creates a new file GDB file with time and date
current_time = datetime.datetime.now().strftime("%Y%m%d%H%M")
gdbname="{}_LAYERSFORPROCESS.gdb".format(current_time)

GDB = arcpy.CreateFileGDB_management(gdbpath,gdbname)

print("created new GDB:", GDB)
print("Step 1 completed successfully! :) ")

#=======================================================================================================================================
print("========== Step 2 ==========")
#Connects to the settings table in the portal 
table = "https://gisportal02.tlv.gov.il/arcgis/rest/services/Hosted/טבלת_הגדרות_לכרטיס_מגרש_ציבורי/FeatureServer/0"
tableFields = [i.name for i in arcpy.ListFields(table)]
dftable = pd.DataFrame.from_records(data=arcpy.da.SearchCursor(table,tableFields),columns=tableFields)

#Connects to migrasim layer, filters the value 1005 and export it to a new layer
migrashim_humim_path = "https://dgt-ags02/arcgis/rest/services/IView2/MapServer/837"
arcpy.FeatureClassToFeatureClass_conversion(migrashim_humim_path, GDB, "migrashim_humim" ,"k_yeud_rashi=1005")
migrashim_humim = str(GDB) + "\\" + "migrashim_humim"
Fieldnames = arcpy.ListFields(migrashim_humim)
stayfields = ["Shape","OBJECTID","Shape_Length","Shape_Area"]
Origfields = ["st_taba","ms_migrash","id_taba","k_yeud_karka","t_yeud_karka"]
for i in Fieldnames:
      if i.baseName not in stayfields and i.baseName not in Origfields :
            arcpy.DeleteField_management(migrashim_humim, i.baseName)

#Intersect each layer with migrasim layer
for layer in dftable.name:
      print ("Now making Intersect of layer {} with migrashim_humim layer.-  Layer {} from {}".format(layer,list(dftable.name).index(layer) + 1,len(dftable.name)))
      outputIntersect = str(GDB) +'\\'+ layer + "Intersect"
      outputLayer = dftable.path[list(dftable.name).index(layer)]
      arcpy.Intersect_analysis((outputLayer,migrashim_humim),outputIntersect,"ALL", None, "INPUT")
      arcpy.AlterField_management(outputIntersect,"FID_migrashim_humim",None,"חופף למגרש")
      Fieldnames = arcpy.ListFields(outputIntersect)
      for i in Fieldnames:
            if i.baseName == "shape_Length":
                  arcpy.AlterField_management(outputIntersect,"shape_Length",None,"Shape_Length")
            if i.baseName in Origfields:
                  arcpy.DeleteField_management(outputIntersect, i.baseName)

            
print("Step 2 completed successfully! :) ")

#=======================================================================================================================================
print("========== Step 3 ==========")  
#migrasim layer:
#List of The layer names
IntersecList = list(dftable.name)
#List of Geometry type
migrashType = [arcpy.Describe(str(GDB) +'\\'+ layer + "Intersect").shapeType for layer in IntersecList] 
#List of unique numbers
migrashlist = [] 
#List of layer area
migrashArealist = []
#A cursor that creates migrashlist and migrashArealist
Cursor = arcpy.SearchCursor(migrashim_humim) 
for row in Cursor:
      migrashlist.append(row.getValue("OBJECTID"))
      migrashArealist.append(row.getValue("Shape_Area"))
      del row
del Cursor 

#Creates an HTML folder. If it exists - deletes and creates a new one
HTML_folder = currentDirectory + "\HTML"
if os.path.exists(HTML_folder):
    shutil.rmtree(HTML_folder)
    os.makedirs(HTML_folder)
else:
    os.makedirs(HTML_folder)

#Converts each layer to a data frame type and puts them all in a list    
dataframelist = []    
for layer in IntersecList:
      outputIntersect = str(GDB) +'\\'+ layer + "Intersect"
      Fieldnames = [i.baseName for i in arcpy.ListFields(outputIntersect)]
      Aliasnames = [i.aliasName for i in arcpy.ListFields(outputIntersect)]
      df = pd.DataFrame.from_records(data=arcpy.da.SearchCursor(outputIntersect,Fieldnames), columns=Aliasnames)
      df = df.replace("NaN", "", regex=True)
      dataframelist.append(df)
      
#Generates an HTML page for each migrash. Each layer has a display type according to the settings table         
for migrash in migrashlist:
      with open(HTML_folder + "\{}.html".format(migrash), "w",encoding="utf-8") as f:
            f.write(f"{settings.TopHTMLurlfilter}\n")
            title = "מגרש {}".format(migrash) 
            f.write('<div id="section{}" class="section">'.format(migrash) + "\n")
            f.write('<h1>{}</h1>'.format(title))
            print ("Now making report to migrash {} ".format(migrash))
            for layer in IntersecList:
                  subtitle =  "שכבת {}:".format(dftable.alias[list(dftable.name).index(layer)])
                  df = dataframelist[IntersecList.index(layer)]
                  rslt_df = df[df['חופף למגרש'] == migrash]
                  layertype = dftable.type[list(dftable.name).index(layer)]
                  if len(rslt_df) > 0:
                        if layertype == "טבלה" :
                              html_table =  rslt_df.to_html(index=False) 
                              # Add the title to the HTML table
                              html_with_subtitle = f'<h3  style="color:Green;">{subtitle} קיימת חפיפה של {len(rslt_df)} רשומות<h3>\n<h4>{html_table}<h4>'
                              f.write(html_with_subtitle + "\n")
                        elif layertype == "כותרת" :
                              if migrashType[IntersecList.index(layer)] == "Polygon" :
                                    analyst = "אחוז השטח החופף - {}%".format(round(rslt_df.drop_duplicates(subset='Shape_Area')['Shape_Area'].sum()/migrashArealist[migrashlist.index(migrash)] *100,2))
                                    f.write(f'<h3  style="color:Green;">{subtitle} קיימת חפיפה של {len(rslt_df)} רשומות. {analyst}<h3>\n')
                              if migrashType[IntersecList.index(layer)] == "Polyline" :  
                                    analyst = f"אורך הקויים בתחום המגרש:{round(rslt_df.drop_duplicates(subset='Shape_Length')['Shape_Length'].sum(),2)} מטר"   
                                    f.write(f'<h3  style="color:Green;">{subtitle} קיימת חפיפה של {len(rslt_df)} רשומות. {analyst}<h3>\n')
                              if migrashType[IntersecList.index(layer)] == "Point" :  
                                    f.write(f'<h3  style="color:Green;">{subtitle} קיימת חפיפה של {len(rslt_df)} רשומות.<h3>\n')                      
            #else:
                  #f.write('<h3  style="color:Red;">{} - לא קיימת חפיפה</h3>'.format(subtitle) + "\n") 
            f.write("<h1>-------------------------------<h1>" +"\n")
            f.write('</div>' + "\n")   
            f.write("<body>" + "\n")
            f.write("<html>" + "\n")
            f.close
                  

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
