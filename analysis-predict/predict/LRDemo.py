# -*- coding: utf-8 -*-

import pandas as pd
import matplotlib
#from pandas.tools.plotting import scatter_matrix
from sklearn.linear_model import LinearRegression

def visualData(dfIncomeTrain):
    font = {
    'family':'SimHei'
    }
    matplotlib.rc('font',**font)
    #scatter_matrix(dfIncomeTrain[["REVENUE_x","COGS","REVENUE_y"]], alpha=0.4)
    dfIncomeTrain[["REVENUE_x","COGS","REVENUE_y"]].corr()

def linearRegression():
    #读取数据
    dfIncomeTrain = pd.read_excel('data/Income Statement train step 1.xls')
    
    #测试集
    dfIncomeTest = dfIncomeTrain[dfIncomeTrain['REVENUE_y'].isna()]
    dfIncomeTest = dfIncomeTest.dropna(1,how='all').dropna(how='any') 
    
    dfIncomeTrain = dfIncomeTrain.dropna(how='any') 
    #检验集
    dfIncomeValidate = dfIncomeTrain[dfIncomeTrain['END_DATE_REP_NEXT_YEAR']=='2017-06-30']
    
    
    dfIncomeTrain = dfIncomeTrain[dfIncomeTrain['END_DATE_REP_NEXT_YEAR']<'2017-06-30']

    #建模
    lrModel = LinearRegression()

    x = dfIncomeTrain[["REVENUE_x","COGS"]]
    y = dfIncomeTrain[["REVENUE_y"]]
    
    #训练模型
    lrModel.fit(x,y)

    #验证模型
    lrModel.predict([[975909000000.29,777147000000.7]])
    lrModel.predict([[74795294306.29,55117487905.7]])
    ndaPreValid = lrModel.predict(dfIncomeValidate[["REVENUE_x","COGS"]])
    dfIncomeValidate["REVENUE_pre"] = ndaPreValid
    dfIncomeValidate.to_excel('data/Income Statement train step 1 validset.xls')
    
    #预测
    ndaPreTest = lrModel.predict(dfIncomeTest[["REVENUE_x","COGS"]])
    dfIncomeTest["REVENUE_pre"] = ndaPreTest
    dfIncomeTest.to_excel('data/Income Statement train step 1 testset.xls')



if __name__=='__main__':
    linearRegression()
