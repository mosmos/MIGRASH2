from datetime import datetime
import os

gdbpath="C:\DEV\GDATA\\{}_LAYERSFORPROCESS.gdb".format(datetime.now().strftime("%Y%m%d"))
datapath="C:\\DEV\\GDATA"
gdbname="{}_LAYERSFORPROCESS.gdb".format(datetime.now().strftime("%Y%m%d"))
connectionpath="C:\DEV\connectionfile\\dgt-sde01db720.sde\\"
excelpath="C:\DEV\connectionfile\MIGRASH_MILON.xlsx"
username = os.getlogin()


