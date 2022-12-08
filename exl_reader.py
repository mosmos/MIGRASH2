import pandas as pd
import os

#The path of the Python file. The Excel file is in the same folder
currentDirectory = os.getcwd()

#Reading the first sheet from the Excel file
df = pd.read_excel(r"{}\MIGRASH_MILON.xlsx".format(currentDirectory), sheet_name=0) 
colunmslist = list(df)
#print(colunmslist)

#Defines a list for each field
#If new fields are added to the Excel file, new lists should be created for them
ALIAS_List = df['ALIAS'].tolist()
PATH_List = df['PATH'].tolist()
SQL_List = df['SQL'].tolist()
ATTRIBUTES_List = df['ATTRIBUTES'].tolist()
BUFFER_List = df['BUFFER'].tolist()
CATEGOR_List = df['CATEGOR'].tolist()
HEB_NAME_List = df['HEB_NAME'].tolist()

#All fields are converted to dictionary values. "ALIAS" field is the key
#If new fields are added to the Excel file, new dictionaries need to be created for them
PATH_dict = {ALIAS_List[i]: PATH_List[i] for i in range(len(ALIAS_List))}
SQL_dict = {ALIAS_List[i]: SQL_List[i] for i in range(len(ALIAS_List))}
ATTRIBUTES_dict = {ALIAS_List[i]: ATTRIBUTES_List[i] for i in range(len(ALIAS_List))}
BUFFER_dict = {ALIAS_List[i]: BUFFER_List[i] for i in range(len(ALIAS_List))}
CATEGOR_dict = {ALIAS_List[i]: CATEGOR_List[i] for i in range(len(ALIAS_List))}
HEB_NAME_dict = {ALIAS_List[i]: HEB_NAME_List[i] for i in range(len(ALIAS_List))}

#==========================================================================================================

#build it like a JSON object - 
# A dictionary within a dictionary..
# where the "ALIAS" column values are the key in the first dictionary

df1 = df #A new dataframe  - a copy of the table

del df1["ALIAS"] #Deleting the ALIAS column so that it does not appear in the second dictionary

dicdf1 = df1.to_dict(orient="records") 

JsonOutput = {ALIAS_List[i]:dicdf1[i] for i in range(len(ALIAS_List))}

print(JsonOutput)






