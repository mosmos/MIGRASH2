import pandas as pd

EXL = r"./MIGRASH_MILON.xlsx"
EXL = pd.read_excel(EXL)

# view the data
#print (EXL.head(3))

# sea the columns
#print (EXL.columns)
print ("*****************************************************")

# filter only specific columns
EXL =  EXL[['PATH','ATTRIBUTES','SQL']]

EXL_dict = EXL.to_dict(orient='records')

print (EXL_dict)

for i in EXL_dict:
    print (i["PATH"])
    print ("---")




