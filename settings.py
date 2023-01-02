from datetime import datetime
import os

gdbpath="C:\DEV\GDATA"
datapath="C:\\DEV\\GDATA"
connectionpath="C:\DEV\connectionfile\\dgt-sde01db720.sde\\"
excelpath="C:\DEV\MIGRASH2\MIGRASH_MILON.xlsx"
username = os.getlogin()
#exltemppath = 'C:\DEV\connectionfile\Report_Temp.xlsx'

def Convert(string):
    li = list(string.split(","))
    return li

#print(gdbpath)
#print(gdbname)


