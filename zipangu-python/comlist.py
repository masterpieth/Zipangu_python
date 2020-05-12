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

def getList(inputText, comtype, model):
    keyword = textToNouns(inputText)
    conn = cx_Oracle.connect("hr/hr@localhost:1521/xe")
    conn.outputtypehandler = OutputTypeHandler
    conn.encoding
    cursor = conn.cursor()
    sql = 'select * from company where type = :param'
    cursor.execute(sql,param=comtype)
    cursor.rowfactory = makeDictFactory(cursor)

    rows = cursor.fetchall()

    df2 = pd.DataFrame(columns=['COMPANY_NUM','TYPE','CONAME','LOCATION','CONTACT','TEXT'])
    
    num = 0
    while num <= len(rows)-1:
        df2.loc[num] = [rows[num]['COMPANY_NUM'],rows[num]['TYPE'],rows[num]['CONAME'],rows[num]['LOCATION'],rows[num]['CONTACT'],rows[num]['TEXT']]
        num += 1

    df2.loc[len(rows)] = ['','','user','','',keyword]

    num = 0
    sim_score_arr = []
    while num <= len(rows):
        text = df2.loc[num]['TEXT'].split(' ')
        keyword = df2.loc[len(rows)]['TEXT'].split(' ')
        sim_value = model.docvecs.similarity_unseen_docs(model,text,keyword,alpha=1,min_alpha=0.0001,steps=5)
        sim_score_arr.append(sim_value)
        num += 1
    df2['SCORE'] = sim_score_arr

    df2 = df2.sort_values(by='SCORE', ascending=False)

    total_result = []
    num = 0
    while num <= len(df2)-1:
        temp_dict = dict()
        temp_dict = {'company_num':df2['COMPANY_NUM'].iloc[num],'type':df2['TYPE'].iloc[num],'coname':df2['CONAME'].iloc[num],'location':df2['LOCATION'].iloc[num],'contact':df2['CONTACT'].iloc[num],'score':df2['SCORE'].iloc[num]}
        total_result.append(temp_dict)
        num +=1
    
    return total_result
