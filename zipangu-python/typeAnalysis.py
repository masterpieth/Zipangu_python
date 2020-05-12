from konlpy.tag import Okt
import cx_Oracle
import os
import pandas as pd
from pandas import DataFrame as df
from datetime import datetime
import numpy as np
from sklearn.metrics.pairwise import linear_kernel
os.environ['NLS_LANG'] = '.UTF8'

def textToNouns(inputText):
    okt = Okt()
    keyword = ' '.join(okt.nouns(inputText))
    return keyword

def makeDictFactory(cursor):
    columnNames = [d[0] for d in cursor.description]

    def createRow(*args):
        return dict(zip(columnNames, args))

    return createRow

def OutputTypeHandler(cursor, name, defaultType, size, precision, scale):
    if defaultType == cx_Oracle.CLOB:
        return cursor.var(cx_Oracle.LONG_STRING, arraysize = cursor.arraysize)

def getTypeList(inputText,listnum,model):
    keyword = textToNouns(inputText)
    conn = cx_Oracle.connect("hr/hr@localhost:1521/xe")
    conn.outputtypehandler = OutputTypeHandler
    conn.encoding
    cursor = conn.cursor()
    sql = 'select * from com_features'
    cursor.execute(sql)
    cursor.rowfactory = makeDictFactory(cursor)

    rows = cursor.fetchall()

    df2 = pd.DataFrame(columns=['TYPE','TEXT'])

    num = 0
    while num <= 125:
        df2.loc[num] = [rows[num]['TYPE'], rows[num]['FEATURES']]
        num +=1

    df2.loc[126] = ['user',keyword]

    num = 0
    sim_score_arr = []
    while num <= 126:
        feature = df2.loc[num]['TEXT'].split(' ')
        keyword = df2.loc[126]['TEXT'].split(' ')
        sim_value = model.docvecs.similarity_unseen_docs(model,feature,keyword,alpha=1,min_alpha=0.0001,steps=5)
        sim_score_arr.append(sim_value)
        num += 1

    df2['SCORE'] = sim_score_arr

    df2 = df2.sort_values(by='SCORE', ascending=False)
    result = df2[['TYPE','SCORE']].iloc[1:int(listnum)]
    
    total_result = []
    
    num = 0
    while num <= len(result)-1:
        temp_dict = dict() 
        temp_dict = {'type':result['TYPE'].iloc[num],'score':result['SCORE'].iloc[num]}
        total_result.append(temp_dict)
        num +=1
    return total_result
