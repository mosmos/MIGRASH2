import pandas as pd

EXL = r"./MIGRASH_MILON.xlsx"
EXL = pd.read_excel(EXL)

# view the data
#print (EXL.head(3))

# sea the columns
#print (EXL.columns)
print ("*****************************************************")

print (EXL[['PATH','BUFFER','ATTRIBUTES']])

print ("*****************************************************")
for i in EXL['PATH']:
    print (EXL[EXL['PATH']==i])

