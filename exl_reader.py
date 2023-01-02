import pandas as pd
import os

#The path of the Python file. The Excel file is in the same folder
currentDirectory = os.getcwd()

#Reading the first sheet from the Excel file
df = pd.read_excel(r"{}\MIGRASH_MILON.xlsx".format(currentDirectory), sheet_name=0) 

ALIAS_List = df['ALIAS'].tolist()

#build it like a JSON object - 
# A dictionary within a dictionary..
# where the "ALIAS" column values are the key in the first dictionary

df1 = df #A new dataframe  - a copy of the table

df1 = df.fillna("") #Replace None to empty string

del df1["ALIAS"] #Deleting the ALIAS column so that it does not appear in the second dictionary

dicdf1 = df1.to_dict(orient="records") 

JsonOutput = {ALIAS_List[i]:dicdf1[i] for i in range(len(ALIAS_List))}

#print(JsonOutput)

