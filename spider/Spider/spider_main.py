# -*- coding: utf-8 -*-


from Spider.Demo import url_manager,html_downloader,html_outputer,html_parser
import xlwt
class SpiderMain(object):
    def __init__(self):
        self.urls=url_manager.UrlManager()
        self.downloader=html_downloader.HtmlDownloader()
        self.parser=html_parser.HtmlParser()
        self.out=html_outputer.output()

    def craw(self,root_url):
        count=1
        self.urls.add_new_url(root_url)
        #while self.urls.has_new_url():
        try:
            new_url=self.urls.get_new_url()
            #print'craw %d : %s'%(count,new_url)
            html_cont=self.downloader.download(new_url)
            #print "111"
            new_urls, new_data = self.parser.parse(new_url, html_cont)
            #print "222"
            #self.urls.add_new_urls(new_urls)
            #print "333"
            self.out.collect_data(new_data)

        except:
            print("爬取失败")
            #except:
                #print 'craw failed'

    def save(self):
        self.out.out2Txt()
        self.out.output_html()
        self.out.out2Excel()
    def trans2Excel(self):
        data_list = []
        title_list =["仪器名称","仪器型号","仪器原值（万元）","资金来源","购置时间"]
        with open('data.txt', 'r', encoding='utf-8') as f:
            a = f.read()
            data_list=list(a)
        file = xlwt.Workbook()
        table = file.add_sheet("其他设备")
        k=0
        for tit in title_list:
            table.write(0,k,tit)
            k+=1
        i=0
        for data in data_list:
           j=0
           print(str(i))
           i += 1
           for s in data:
               table.write(i,j,s)
               j+=1

        file.save('data.xls')
if __name__ == "__main__":
    i = 0
    cont = 1
    root_url="http://zyjs.sgst.cn/xxgk/platform!plfmList.do"
    root_url = "http://zyjs.sgst.cn/xxgk/platform!plfmList.do"
    obj_spider=SpiderMain()
    while cont <= 2:
        print(str(cont))
        obj_spider.craw(root_url)
        #i = int(i)
        i = i + 8
        #i = bytes(i)
        root_url = r"http://zyjs.sgst.cn/xxgk/platform!plfmList.do?offset="+str(i)
        #urllib.parse.urljoin(r"http://zyjs.sgst.cn/xxgk/platform!plfmList.do?offset=",i )
        cont = cont + 1
    obj_spider.save()

        # with open('data.txt', 'r', encoding='utf-8') as f:
        #     a=f.read()
        #     print(a)
        #     b = list(a)
        #     print(len(b))



