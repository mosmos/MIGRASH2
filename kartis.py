import time
import datetime
import arcpy
import pandas as pd
import shutil
import os
import logging
import sys
import requests
import html
import send2trash

# Define project location
currentDirectory = os.getcwd()
current_time = datetime.datetime.now().strftime("%Y%m%d%H%M")

# create a logger that is a child of the root logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# set up a console handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)
console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)

# set up a file handler
file_handler = logging.FileHandler('C:\DEV\LOG\logfile{}.log'.format(current_time)) #In gisdev01 - "C:\Jonathan_Dell\LOG\logfile{}.log"
file_handler.setLevel(logging.INFO)
file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

logger.info(time.ctime())
st = time.time()
logger.info("========== Step 1 ==========")

#Defines the code and project path 
gdbpath = "C:\DEV\GDATA"  #In gisdev01 - "C:\Jonathan_Dell\GDATA"
username = os.getlogin()

logger.info("Hello {}!".format(username))
logger.info(currentDirectory)
   
#Creates a new file GDB file with time and date
gdbname="{}_LAYERSFORPROCESS.gdb".format(current_time)
GDB = arcpy.CreateFileGDB_management(gdbpath,gdbname)

logger.info("created new GDB:", GDB)

#Deleting files created more than a week ago
current_date = datetime.datetime.now()

# Loop through all files in the folder
for filename in os.listdir(gdbpath):

    # Check if the file is a GDB file
    if filename.endswith(".gdb"):

        # Extract the creation date from the file name
        creation_date_str = filename.split("_")[0]
        creation_date = datetime.datetime.strptime(creation_date_str, "%Y%m%d%H%M")

        # Calculate the number of days since the file was created
        delta = current_date - creation_date
        days_since_creation = delta.days

        # If the file is more than 7 days old, delete it
        if days_since_creation > 7:
            file_path = os.path.join(gdbpath, filename)
            #shutil.rmtree(file_path)
            send2trash.send2trash(file_path)
            logger.info(f"Deleted file: {filename}")

logger.info("Step 1 completed successfully! :) ")
#=======================================================================================================================================
logger.info("========== Step 2 ==========")
#Connects to the settings table in the portal 
table = "https://gisportal02.tlv.gov.il/arcgis/rest/services/Hosted/טבלת_הגדרות_לכרטיס_מגרש_ציבורי/FeatureServer/0"
tableFields = [i.name for i in arcpy.ListFields(table)]
dftable = pd.DataFrame.from_records(data=arcpy.da.SearchCursor(table,tableFields),columns=tableFields)
dftable = dftable[dftable['name'] != ""]

#Connects to migrasim layer and export it to a new layer
migrashim_humim_path = "https://gisportal02.tlv.gov.il/arcgis/rest/services/%D7%9E%D7%92%D7%A8%D7%A9%D7%99%D7%9D_%D7%97%D7%95%D7%9E%D7%99%D7%9D_%D7%9C%D7%9B%D7%A8%D7%98%D7%99%D7%A1_%D7%9E%D7%92%D7%A8%D7%A9_%D7%A6%D7%99%D7%91%D7%95%D7%A8%D7%99/FeatureServer/0"
arcpy.FeatureClassToFeatureClass_conversion(migrashim_humim_path, GDB, "migrashim_humim",None)
migrashim_humim = str(GDB) + "\\" + "migrashim_humim"
Fieldnames = arcpy.ListFields(migrashim_humim)
stayfields = ["Shape","OBJECTID","Shape_Length","Shape_Area","Name"]
#Deletes all fields except those in the "stayfields" list
for i in Fieldnames:
      if i.baseName not in stayfields:
            arcpy.DeleteField_management(migrashim_humim, i.baseName)

#Intersect each layer with migrasim layer
for layer in dftable.name:
      logger.info ("Now making Intersect of layer {} with migrashim_humim layer.-  Layer {} from {}".format(layer,list(dftable.name).index(layer) + 1,len(dftable.name)))
      outputIntersect = str(GDB) +'\\'+ layer + "Intersect"
      outputLayer = dftable.path[list(dftable.name).index(layer)]
      arcpy.Intersect_analysis((outputLayer,migrashim_humim),outputIntersect,"ALL", None, "INPUT")
      arcpy.AlterField_management(outputIntersect,"Name",None,"חופף למגרש")
                  
logger.info("Step 2 completed successfully! :) ")
#=======================================================================================================================================
logger.info("========== Step 3 ==========")  
#List of The layers names
IntersecList = list(dftable.name)
logger.info("A list of the layers names is ready") 
 #List of The attributes names
attributesList = list(dftable.attributes)
logger.info("A list of the attributes is ready") 
#List of Geometry type
migrashType = [arcpy.Describe(str(GDB) +'\\'+ layer + "Intersect").shapeType for layer in IntersecList] 
logger.info("A list of Geometry type of each layer is ready")  
#List of unique numbers
migrashlist = [] 
#List of layer area
migrashArealist = []
#A cursor that creates migrashlist and migrashArealist
Cursor = arcpy.SearchCursor(migrashim_humim) 
for row in Cursor:
      migrashlist.append(row.getValue("Name"))
      migrashArealist.append(row.getValue("Shape_Area"))
      del row
del Cursor 

logger.info("A list of unique numbers of migrasim layer is ready") 
logger.info("A list of areas of migrasim layer is ready") 

#Defines the HTML folder.
HTML_folder = "\\\\dgt-ags01\\kartismigrash"
logger.info("HTML folder - " + " {}".format(HTML_folder)) 

#Converts each layer to a dataframe type and puts them all in a list    
dataframelist = []    
for layer in IntersecList:
      outputIntersect = str(GDB) +'\\'+ layer + "Intersect"
      Fieldnames = [i.baseName for i in arcpy.ListFields(outputIntersect)]
      Aliasnames = [i.aliasName for i in arcpy.ListFields(outputIntersect)]
      df = pd.DataFrame.from_records(data=arcpy.da.SearchCursor(outputIntersect,Fieldnames), columns=Aliasnames)
      df = df.replace("NaN", "", regex=True) #replace Nan with empty string
      dataframelist.append(df)
      
logger.info("All layers have been converted to a dataframe within a list") 

#The beginning of the HTML which includes various definitions such as utf-8, font and more
TopHTMLurlfilter = """
<!DOCTYPE html>
<meta charset="UTF-8">
<html>
<html dir="rtl" lang="ar"></html>
<head>
  <style>
    body {
      font-family: 'Calibri', sans-serif;
    }
  </style>
  <title>כרטיס מגרש ציבורי</title>
    <script>
      function getUrlParameter(name) {
        name = name.replace(/[\[]/, '\\[').replace(/[\]]/, '\\]');
        var regex = new RegExp('[\\?&]' + name + '=([^&#]*)');
        var results = regex.exec(location.search);
        return results === null
          ? ''
          : decodeURIComponent(results[1].replace(/\+/g, ' '));
      }
      window.onload = function() {
        var sectionId = getUrlParameter('section');
        if (sectionId) {
          var sections = document.getElementsByClassName('section');
          for (var i = 0; i < sections.length; i++) {
            if (sections[i].id === sectionId) {
              sections[i].style.display = 'block';
            } else {
              sections[i].style.display = 'none';
            }
          }
        }
      };
    </script>
  </head>
  <body>
"""
      
#Generates an HTML page for each migrash. Each layer has a display type according to the settings table - "טבלה" or "כותרת".   
logger.info("Starting to Generate an HTML page for each migrash")       
for migrash in migrashlist:
      with open(HTML_folder + "\{}.html".format(migrash), "w",encoding="utf-8") as f:
            f.write(f"{TopHTMLurlfilter}\n") #Writes the beginning of the HTML
            title = "מגרש {}".format(migrash) 
            f.write('<div id="section{}" class="section">'.format(migrash) + "\n")
            f.write('<h1>{}</h1>'.format(title) + "\n") #Title - migrash number
            f.write('<h3  style="color:Red;">עדכון אחרון {}</h3>'.format(datetime.datetime.now().strftime("%d/%m/%Y %H:%M")) + "\n") #Writes the the current time 
            logger.info ("Now making report to migrash {} , {} from {}".format(migrash,migrashlist.index(migrash),len(migrashlist)))
            for layer in IntersecList:
                  subtitle =  "{}".format(dftable.alias[list(dftable.name).index(layer)]) #subtitle - Layer name
                  df = dataframelist[IntersecList.index(layer)]
                  rslt_df = df[df['חופף למגרש'] == migrash] #Leaving only the records that overlap with migrash
                  layertype = dftable.type[list(dftable.name).index(layer)] #Checks the card type from the settings table
                  if len(rslt_df) > 0: #That is, when there is an overlap between the layer and migrash
                        f.write('<h2  style="color:Black;">{} (שכבה מספר {}):<h2>\n'.format(subtitle, IntersecList.index(layer) + 1)) #Writes the layer name
                        if layertype == "טבלה" :
                              columns_to_keep = attributesList[IntersecList.index(layer)].split(",") #Checks which fields to leave according to what appears in the settings table
                              df = df.filter(columns_to_keep)
                              rslt_df = rslt_df.filter(columns_to_keep)
                              html_table =  rslt_df.to_html(index=False) 
                              # Add the title to the HTML table
                              html_with_subtitle = f'<h3  style="color:Green;">&#x2713; {len(rslt_df)} רשומות<h3>\n<h4  style="color:Green;">{html_table}<h4>'
                              f.write(html_with_subtitle + "\n") #Writes in HTML the amount of overlapping records and the table
                        elif layertype == "פירוט" : 
                              #Here we need to separate the geometry types:
                              #If the layer is polygon type - calculate the overlap ratio with the layer.
                              #If the layer is line type - calculate the length of the line passing through migrash.
                              #If the layer is of point type - we will show only the overlapping records
                              if migrashType[IntersecList.index(layer)] == "Polygon" :
                                    last_column_name = df.columns[-1]
                                    analyst = "אחוז השטח החופף - {}%".format(round(rslt_df.drop_duplicates(subset = last_column_name)[last_column_name].sum()/migrashArealist[migrashlist.index(migrash)] *100,2))
                                    f.write(f'<h3  style="color:Green;">&#x2713; {len(rslt_df)} רשומות. {analyst}<h3>\n')
                              if migrashType[IntersecList.index(layer)] == "Polyline" :  
                                    last_column_name = df.columns[-1]
                                    analyst = f"אורך הקויים בתחום המגרש:{round(rslt_df.drop_duplicates(subset = last_column_name)[last_column_name].sum(),2)} מטר"   
                                    f.write(f'<h3  style="color:Green;">&#x2713; {len(rslt_df)} רשומות. {analyst}<h3>\n')
                              if migrashType[IntersecList.index(layer)] == "Point" :  
                                    f.write(f'<h3  style="color:Green;">&#x2713; {len(rslt_df)} רשומות.<h3>\n') 
                        elif layertype == "יש/אין" :
                              #Just to know if there is an overlap
                              f.write(f'<h3  style="color:Green;">&#x2713;<h3>\n')                                                       
            f.write("<h1>-------------------------------<h1>" +"\n")
            f.write('</div>' + "\n")   
            f.write("<body>" + "\n")
            f.write("<html>" + "\n")
            f.close
                  

logger.info("Step 3 completed successfully!")
#=======================================================================================================================================
logger.info("========== Step 4 ==========")

#Update the time of the settings table
with arcpy.da.UpdateCursor(table, ['time']) as cursor:
    for row in cursor:
        row[0] = datetime.datetime.now()
        cursor.updateRow(row)
logger.info("Update the time of the settings table")

#Get the update alias name of every layer from Iview2 API 
layernames = []
pathlist = dftable["path"].values.tolist()
for path in pathlist:
  response = requests.get(path)
  html_source = response.text
  start_index = html_source.find("Layer: ") + 7
  end_index = html_source.find("(ID")
  decoded_text = html.unescape(html_source[start_index:end_index])
  layernames.append(decoded_text)
  
#Update the Layers names in the settings table
with arcpy.da.UpdateCursor(table, ['alias']) as cursor:
  for index, row in enumerate(cursor):
    if index < (len(layernames)):
      row[0] = layernames[index]
      cursor.updateRow(row)
logger.info("Update the Layers names in the settings table")
    

et = time.time()
res = et - st
final_res = str(res / 60)
logger.info("Done!")
logger.info("Good work {}! ".format(username))
logger.info("\N{smiling face with sunglasses}")
logger.info(time.ctime())
logger.info('Execution time:', final_res[0:final_res.find(".") + 3], 'minutes')
