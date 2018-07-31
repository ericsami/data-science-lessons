#coding:utf8

import  xlwt
class output(object):
    def __init__(self):
        self.datas = []

    def collect_data(self,data):
        if data is None:
            return
        self.datas.extend(data)

    def output_html(self):
        fout=open('output.html','w',encoding='utf-8')
        fout.write('<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">')
        fout.write("<html>")
        fout.write("<body>")
        fout.write("<table>")
        for data in self.datas:
            fout.write("<tr>")
            for s in data:
                fout.write("<td>%s</td>" % s)
            fout.write("</tr>")
        fout.write("</table>")
        fout.write("</body>")
        fout.write("</html>")
        fout.close()

    def out2Txt(self):
        print(len(self.datas))
        with open('data.txt','a',encoding='utf-8') as f:
               for data in self.datas:
                   f.write(str(data)+"\n")
        print('successful')

    def out2Excel(self):
        data_list = []
        title_list =["专业技术服务平台","仪器名称","仪器型号","仪器原值（万元）","资金来源","购置时间"]
        # with open('data.txt', 'r', encoding='utf-8') as f:
        #     a = f.read()
        #     data_list=list(a)
        file = xlwt.Workbook()
        table = file.add_sheet("其他设备")
        k=0
        for tit in title_list:
            table.write(0,k,tit)
            k+=1
        i=0
        for data in self.datas:
           j=0
           #print(str(i))
           i += 1
           for s in data:
               table.write(i,j,s)
               j+=1

        file.save('data.xls')


