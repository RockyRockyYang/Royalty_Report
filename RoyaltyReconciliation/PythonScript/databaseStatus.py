import cx_Oracle
import sys

#This file do a simple test to check the database status
#It is written in python to simulate the step of calling the python script 
# database:maker@BIREPORA1D.imo-online.com
# password:maker
db='maker/maker@BIREPORA1D.imo-online.com'
connection=None
connection = cx_Oracle.Connection(db)
try:
    connection.ping()
    print("true")
except cx_Oracle.InterfaceError as e:
    print(e, file=sys.stderr)
    sys.exit(1)
except Exception as e:
    print(e, file=sys.stderr)
    sys.exit(1)