#-*- coding: utf-8 -*-

import os

from extract.ZengJianChiExtractor import ZengJianChiExtractor
from extract.DingZengExtractor import DingZengExtractor

def print_2d_dict(rs_dict):
    if rs_dict is None:
        return
    for (row_id, row) in sorted(rs_dict.items()):
        print(row_id, " => ", sorted(row.items()))


def test_html_parser_table(html_parser, html_file_path):
    for table_dict in html_parser.parse_table(html_file_path):
        print_2d_dict(table_dict)
        print('-' * 80)


def test_html_parser_paragraph(html_parser, html_file_path):
    for paragraph in html_parser.parse_content(html_file_path):
        print(paragraph)


def test_zjc_content_extract(zjc_ex):
    paras = [
        "2014年5月27日，本公司接到控股股东彩虹集团电子股份有限公司（以下简称“彩虹电子”）通知，彩虹电子于2014年3月25日通过上海证券交易所大宗交易系统出售了本公司无限售条件流通股股份500万股，占公司股份总数的0.6786%，均价100元；于2014年5月26日通过上海证券交易所大宗交易系统出售了本公司无限售条件流通股股份500万股，占公司股份总数的0.6786%，合计减持1000万股，占公司股份总数的1.357% ",
        "上述两次减持前，彩虹电子持有本公司股份165004798股，占公司股份总数的22.40% ；本次减持后，彩虹电子持有本公司股份155004798股，占公司股份总数的21.04% 。"]
    for record in zjc_ex.extract_from_paragraphs(paras):
        print(record.to_result())
    print(zjc_ex.com_abbr_dict)
    print(zjc_ex.com_full_dict)

def test_dz_content_extract(dz_ex):
    paras = ["本次非公开发行股票的发行对象为深圳市华融泰资产管理有限公司，为公司第二大股东，持有公司17.41%的股权。", 
          "本次非公开发行股票的数量拟为11,000万股，发行对象拟以人民币现金方式认购。发行对象认购本次发行的股票自发行结束之日起36个月内不上市交易或转让。",
          "本次非公开发行股票发行价格为4.81元/股，根据《上市公司证券发行管理办法》、《上市公司非公开发行股票实施细则》等法律、法规、规范性文件的有关规定，本次非公开发行股票的发行价格不低于定价基准日前二十个交易日公司股票均价的90%（定价基准日前20个交易日股票交易均价＝定价基准日前20个交易日股票交易总额/定价基准日前20个交易日股票交易总量）。"]
    for record in dz_ex.extract_from_paragraphs(paras):
        print(record.to_result())

#######################################################################################################################

def extract_dingzeng(dz_ex, html_dir_path, html_id):
    record_list = []
    for record in dz_ex.extract(os.path.join(html_dir_path, html_id)):
        if record is not None and record.ZengFaDuiXiang is not None and \
                len(record.ZengFaDuiXiang) > 1  and (record.ShuLiang is not None or record.JinE is not None):
            record_list.append("%s\t%s" % (html_id.replace(".html",""), record.to_result()))
    for record in record_list:
        print(record)
    return record_list


def extract_dingzeng_from_html_dir(dz_ex, html_dir_path):
    print('公告id\t增发对象\t增发数量\t增发金额\t锁定期\t认购方式')
    for html_id in os.listdir(html_dir_path):
        extract_dingzeng(dz_ex, html_dir_path, html_id)


def extract_zengjianchi(zjc_ex, html_dir_path, html_id):
    record_list = []
    for record in zjc_ex.extract(os.path.join(html_dir_path, html_id)):
        if record is not None and record.shareholderFullName is not None and \
                len(record.shareholderFullName) > 1 and \
                record.finishDate is not None and len(record.finishDate) >= 6:
            record_list.append("%s\t%s" % (html_id.replace(".html",""), record.to_result()))
    for record in record_list:
        print(record)
    return record_list


def extract_zengjianchi_from_html_dir(zjc_ex, html_dir_path):
    print('公告id\t股东全称\t股东简称\t变动截止日期\t变动价格\t变动数量\t变动后持股数\t变动后持股比例')
    for html_id in os.listdir(html_dir_path):
        extract_zengjianchi(zjc_ex, html_dir_path, html_id)

def extract_zengjianchi_from_html_dir2(zjc_ex, html_dir_path):
    print('公告id\t股东全称\t股东简称\t变动截止日期\t变动价格\t变动数量\t变动后持股数\t变动后持股比例')
    for html_id in os.listdir(html_dir_path):
        extract_zengjianchi(zjc_ex, html_dir_path, html_id)


if __name__ == "__main__":

    ner_model_dir_path = 'model/ltp_data_v3.3.1'
    ner_blacklist_file_path = 'config/ner_com_blacklist.txt'

    dingzeng_config_file_path = 'config/DingZengConfig.json'
    dz_ex = DingZengExtractor(dingzeng_config_file_path, ner_model_dir_path, ner_blacklist_file_path)
    extract_dingzeng_from_html_dir(dz_ex, 'data/dingzeng_html')
    #test_dz_content_extract(dz_ex)

    zengjianchi_config_file_path = 'config/ZengJianChiConfig.json'
    zjc_ex = ZengJianChiExtractor(zengjianchi_config_file_path, ner_model_dir_path, ner_blacklist_file_path)
    #extract_zengjianchi_from_html_dir(zjc_ex, 'data/zengjianchi_html')
    #test_zjc_content_extract(zjc_ex)

    
