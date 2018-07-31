
import math
import pandas as pd

def validLr():
    dfIncomeValidate = pd.read_excel('data/Income Statement train step 1 validset.xls')
    #获取5月31日收盘价
    dfMarketData = pd.read_excel('data/[New] Market Data_20180613.xlsx')
    dfMarketData = dfMarketData[dfMarketData['END_DATE_']=='2018/5/31']
    dfMarketData.to_excel('data/Market Data 2018-05-31.xls')

    dfMarketData = pd.read_excel('data/Market Data 2018-05-31.xls')

    dfIncomeValidate = pd.merge(dfIncomeValidate, dfMarketData, on=['TICKER_SYMBOL'], how='left')
    dfIncomeValidate["BaseError"] = dfIncomeValidate.apply(lambda x: 0.8*math.log(max(x['CLOSE_PRICE'],2),2),axis= 1)
    dfIncomeValidate["PreError"] = dfIncomeValidate.apply(lambda x: min(abs(x['REVENUE_pre']/(x['REVENUE_y']+0.1)-1),0.8)*math.log(max(x['CLOSE_PRICE'],2),2),axis= 1)
    
    dfIncomeValidate.to_excel('data/Income Statement train step 2 validset.xls')

    baseError = dfIncomeValidate["BaseError"].sum()
    preError = dfIncomeValidate["PreError"].sum()

    score = format(preError/baseError,'.2f')
    print("得分:", score)
    score2 = dfIncomeValidate["PreError"].sum()/len(dfIncomeValidate)
    print("得分2:", score2)

if __name__=='__main__':
    validLr()