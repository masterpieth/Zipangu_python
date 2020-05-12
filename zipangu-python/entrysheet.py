import cx_Oracle
import os
import pandas as pd
from konlpy.tag import Okt

os.environ['NLS_LANG'] = '.UTF8'
def makeDictFactory(cursor):
    columnNames = [d[0] for d in cursor.description]

    def createRow(*args):
        return dict(zip(columnNames, args))

    return createRow

def OutputTypeHandler(cursor, name, defaultType, size, precision, scale):
    if defaultType == cx_Oracle.CLOB:
        return cursor.var(cx_Oracle.LONG_STRING, arraysize = cursor.arraysize)

conn = cx_Oracle.connect("hr/hr@localhost:1521/xe")
conn.outputtypehandler = OutputTypeHandler
conn.encoding
cursor = conn.cursor()

def getTotalList():
    sql = 'select * from entrysheet order by entrysheet_num'
    cursor.execute(sql)
    cursor.rowfactory = makeDictFactory(cursor)

    rows = cursor.fetchall()
    
    return rows

def searchEntrysheet(jobType):
    param = "%"+jobType+"%"
    sql = "select * from entrysheet where jobtype like :param"
    cursor.execute(sql,{'param':param})
    cursor.rowfactory = makeDictFactory(cursor)
    rows = cursor.fetchall()
    
    return rows
