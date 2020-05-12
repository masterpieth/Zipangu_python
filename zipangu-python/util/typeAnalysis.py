from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from konlpy.tag import Kkma
import cx_Oracle
import os
import pandas as pd
from pandas import DataFrame as df
from datetime import datetime
import numpy as np
from sklearn.metrics.pairwise import linear_kernel
os.environ['NLS_LANG'] = '.UTF8'

def textToNouns(inputText):
    kkma = Kkma()
    keyword = ' '.join(kkma.nouns(inputText))
    return keyword

def makeDictFactory(cursor):
    columnNames = [d[0] for d in cursor.description]

    def createRow(*args):
        return dict(zip(columnNames, args))

    return createRow

def OutputTypeHandler(cursor, name, defaultType, size, precision, scale):
    if defaultType == cx_Oracle.CLOB:
        return cursor.var(cx_Oracle.LONG_STRING, arraysize = cursor.arraysize)

def getTypeList(inputText,listnum):
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
        num += 1

    df1 = df(data={'TYPE':['user'],'TEXT':keyword})
    df2.loc[126] = ['user',keyword]
    
    tfidf = TfidfVectorizer()
    tfidf_matrix = tfidf.fit_transform(df2['TEXT'])
    tfidf_matrix = tfidf_matrix.astype(np.float32)
    cosine_sim = linear_kernel(tfidf_matrix,tfidf_matrix)
    indices = pd.Series(df2.index, index=df2['TYPE']).drop_duplicates()
    
    idx = indices['user']
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    listnum = int(listnum) + 1
    sim_scores = sim_scores[1:listnum]
    text_indices = [i[0] for i in sim_scores]
    result = df2['TYPE'].iloc[text_indices]
    type_arr = []
    num = 0
    while num <= len(result) -1:
        type_arr.append(result.iloc[num])
        num += 1
    result_dict = {'type': type_arr}
    return result_dict
