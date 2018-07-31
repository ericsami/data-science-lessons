# -*- coding: utf-8 -*-

import calendar
import time
import datetime
import pandas as pd

def createTrainData():
    #读取工业企业利润表
    dfIncome = pd.read_excel('data/Income Statement100.xls')
    dfIncome = dfIncome[['PARTY_ID','TICKER_SYMBOL','EXCHANGE_CD','END_DATE_REP','END_DATE','T_REVENUE','REVENUE','T_COGS','COGS']]
    #抽取所有第二季度的数据
    dfIncome = dfIncome[dfIncome['END_DATE_REP'].apply(lambda x:'-06-30' in x)]
    #添加预测结果数据列
    dfIncome['END_DATE_REP_NEXT_YEAR'] = dfIncome['END_DATE_REP'].apply(lambda x: datetime.datetime(time.strptime(x,'%Y-%m-%d').tm_year+1,time.strptime(x,'%Y-%m-%d').tm_mon,time.strptime(x,'%Y-%m-%d').tm_mday).strftime('%Y-%m-%d')) 
    
    #下一年的营业收入
    dfRevenueNextYear = dfIncome[['PARTY_ID','END_DATE_REP','REVENUE']]
    dfRevenueNextYear.rename(columns={'END_DATE_REP':'END_DATE_REP_NEXT_YEAR'}, inplace = True)
    #合并生成训练集
    dfIncomeTrain = pd.merge(dfIncome, dfRevenueNextYear, on=['PARTY_ID','END_DATE_REP_NEXT_YEAR'], how='left')
    #简单去重（如果根据实际，则需要保留重复记录的最后一条）
    dfIncomeTrain = dfIncomeTrain.drop_duplicates(['PARTY_ID','END_DATE_REP'])
    #保存中间文件
    dfIncomeTrain.to_excel('data/Income Statement train step 1.xls')


if __name__=='__main__':
    createTrainData()