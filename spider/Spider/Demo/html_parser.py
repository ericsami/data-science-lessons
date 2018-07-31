#coding:utf8
from bs4 import BeautifulSoup
import re

from Spider.Demo import  html_downloader
import urllib.request
class HtmlParser(object):

    def _get_new_urls(self, page_url, soup):
        new_urls = set()
        links=soup.find_all('a', href = re.compile(r"platform!baseInfo"))
        for link in links:
            #print(link)
            new_url = link['href'].replace("baseInfo", "resourceInfo")
            new_full_url = urllib.parse.urljoin("http://zyjs.sgst.cn/xxgk/", new_url)
            #urllib.parse.urljoin(page_url, new_url)
            #print(new_full_url)
            new_urls.add(new_full_url)
        return new_urls

    def _get_new_data(self, page_url, soup):
        res_data=[]
        platform = soup.find('p',{'class':'xxgk_h1'})

        title_node = soup.find_all('table')[2]#先找到所有的table，页面一共有三个，拿最后一个就是我们要的
        table =title_node.contents[3:-1:2]#通过断点发现contents就是我们要的内容，不过是间隔的，从第4个开始跳1行取一个
        #print(table)

        for node in table:
            text = node.text
            data =  text.replace("\t","").replace("\r","").replace("\n\n","").split("\n")#去除换行符制表符等
            print(data)
            data_add=[]
            data_add.append(platform.text)
            data_add.extend(data)
            res_data.append(data_add)

        #title_node = soup.find('dd', class_="lemmaWgt-lemmaTitle-title").find("h1")
        # res_data['title']=title_node.get_text()
        # summary_node = soup.find('tr')
        # res_data['summary'] = summary_node.get_text()
        return res_data

    def parse(self, page_url, html_cont):
        if page_url is None or html_cont is None:
            return

        soup = BeautifulSoup(html_cont, 'html.parser', from_encoding =  'utf-8')
        new_urls = self._get_new_urls(page_url, soup)

        new_datas = []
        for url in new_urls:
            data_html = html_downloader.HtmlDownloader().download(url)
            soup = BeautifulSoup(data_html, 'html.parser', from_encoding='utf-8')
            new_data = self._get_new_data(url, soup)
            new_datas.extend(new_data)
        return new_urls, new_datas
