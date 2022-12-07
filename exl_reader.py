import pandas as pd
import os

#The path of the Python file. The Excel file is in the same folder
currentDirectory = os.getcwd()

#Reading the first sheet from the Excel file
df = pd.read_excel(r"{}\MIGRASH_MILON.xlsx".format(currentDirectory), sheet_name=0) 

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

# MY: build it like a JSON object
# { layer_name(KEY) : {SQL:"",ATT:"",BUFFER:"",....}

#A few prints for testing
print(PATH_dict)
print(SQL_dict)
print(HEB_NAME_dict)






