#-*- coding: utf-8 -*-

import codecs
import json
import re

from docparser import HTMLParser
from utils import TextUtils
from ner import NERTagger


class DingZengRecord(object):
    def __init__(self, ZengFaDuiXiang,FaXingFangShi,ShuLiang,JinE,ShuoDingQi,RenGouFangShi):
        #增发对象
        self.ZengFaDuiXiang = ZengFaDuiXiang
        #增发数量
        self.ShuLiang = ShuLiang
        #增发金额
        self.JinE = JinE
        #锁定期
        self.ShuoDingQi = ShuoDingQi
        #认购方式
        self.RenGouFangShi = RenGouFangShi

    def __str__(self):
        return json.dumps(self.__dict__, ensure_ascii=False)

    def normalize_num(self, text):
        coeff = 1.0
        if '亿' in text:
            coeff *= 100000000
        if '万' in text:
            coeff *= 10000
        if '千' in text or '仟' in text:
            coeff *= 1000
        if '百' in text or '佰' in text:
            coeff *= 100
        if '%' in text:
            coeff *= 0.01
        try:
            number = float(TextUtils.extract_number(text))
            number_text = '%.4f' % (number * coeff)
            if number_text.endswith('.0'):
                return number_text[:-2]
            elif number_text.endswith('.00'):
                return number_text[:-3]
            elif number_text.endswith('.000'):
                return number_text[:-4]
            elif number_text.endswith('.0000'):
                return number_text[:-5]
            else:
                if '.' in number_text:
                    idx = len(number_text)
                    while idx > 1 and number_text[idx-1] == '0':
                        idx -= 1
                    number_text = number_text[:idx]
                return number_text
        except:
            return text

    def normalize(self):
        if self.ShuLiang is not None:
            self.ShuLiang = self.normalize_num(self.ShuLiang)
        if self.JinE is not None:
            self.JinE = self.normalize_num(self.JinE)

    def to_result(self):
        self.normalize()
        return "%s\t%s\t%s\t%s\t%s" % (
            self.ZengFaDuiXiang if self.ZengFaDuiXiang is not None else '',
            self.ShuLiang if self.ShuLiang is not None else '',
            self.JinE if self.JinE is not None else '',
            self.ShuoDingQi if self.ShuoDingQi is not None else '',
            self.RenGouFangShi if self.RenGouFangShi is not None else '')


class DingZengExtractor(object):
    def __init__(self, config_file_path, ner_model_dir_path, ner_blacklist_file_path):
        self.html_parser = HTMLParser.HTMLParser()
        self.config = None
        self.ner_tagger = NERTagger.NERTagger(ner_model_dir_path, ner_blacklist_file_path)
        self.com_abbr_dict = {}
        self.com_full_dict = {}
        self.com_abbr_ner_dict = {}

        self.RenGouFangShi = None

        with codecs.open(config_file_path, encoding='utf-8', mode='r') as fp:
            self.config = json.loads(fp.read())
        self.table_dict_field_pattern_dict = {}
        for table_dict_field in self.config['table_dict']['fields']:
            field_name = table_dict_field['fieldName']
            if field_name is None:
                continue
            convert_method = table_dict_field['convertMethod']
            if convert_method is None:
                continue
            pattern = table_dict_field['pattern']
            if pattern is None:
                continue
            col_skip_pattern = None
            if 'colSkipPattern' in table_dict_field:
                col_skip_pattern = table_dict_field['colSkipPattern']
            row_skip_pattern = None
            if 'rowSkipPattern' in table_dict_field:
                row_skip_pattern = table_dict_field['rowSkipPattern']
            self.table_dict_field_pattern_dict[field_name] = \
                TableDictFieldPattern(field_name=field_name, convert_method=convert_method,
                                      pattern=pattern, col_skip_pattern=col_skip_pattern,
                                      row_skip_pattern=row_skip_pattern)

    

    def extract_from_table_dict(self, table_dict):
        rs = []
        if table_dict is None or len(table_dict) <= 0:
            return rs
        row_length = len(table_dict)
        field_col_dict = {}
        skip_row_set = set()
        # 1. 假定第一行是表头部分则尝试进行规则匹配这一列是哪个类型的字段
        # 必须满足 is_match_pattern is True and is_match_col_skip_pattern is False
        head_row = table_dict[0]
        col_length = len(head_row)
        for i in range(col_length):
            text = head_row[i]
            for (field_name, table_dict_field_pattern) in self.table_dict_field_pattern_dict.items():
                if table_dict_field_pattern.is_match_pattern(text) and \
                        not table_dict_field_pattern.is_match_col_skip_pattern(text):
                    if field_name not in field_col_dict:
                        field_col_dict[field_name] = i
                    # 逐行扫描这个字段的取值，如果满足 row_skip_pattern 则丢弃整行 row
                    for j in range(1, row_length):
                        try:
                            text = table_dict[j][i]
                            if table_dict_field_pattern.is_match_row_skip_pattern(text):
                                skip_row_set.add(j)
                        except KeyError:
                            pass
        if len(field_col_dict) <= 0:
            return rs
        # 2. 遍历每个有效行，获取 record
        for row_index in range(1, row_length):
            if row_index in skip_row_set:
                continue
            record = DingZengRecord(None, None, None, None, None, self.RenGouFangShi)
            for (field_name, col_index) in field_col_dict.items():
                try:
                    text = table_dict[row_index][col_index]
                    if field_name == 'ZengFaDuiXiang':
                        record.ZengFaDuiXiang = self.table_dict_field_pattern_dict.get(field_name).convert(text)
                    elif field_name == 'ShuLiang':
                        record.ShuLiang = self.table_dict_field_pattern_dict.get(field_name).convert(text)
                    elif field_name == 'JinE':
                        record.JinE = self.table_dict_field_pattern_dict.get(field_name).convert(text)
                    else:
                        pass
                except KeyError:
                    pass
            rs.append(record)
        return rs

    def extract_from_paragraphs2(self, paragraphs):
        record_list = []
        return record_list

    
    def extract_from_paragraphs(self, paragraphs):
        record_list = []
        change_records = []
        for para in paragraphs:
            if para != "":
                change_records_para = self.extract_from_paragraph(para)
                change_records += change_records_para
        for record in change_records:
            record_list.append(record)
        return record_list

    def extract_from_paragraph(self, paragraph):
        #tag_res = self.ner_tagger.ner(paragraph, self.com_abbr_ner_dict)
        #tagged_str = tag_res.get_tagged_str()
        self.extract_RenGouFangShi(paragraph)
        return []

    def extract_RenGouFangShi(self, paragraph):
        if paragraph.find("现金") != -1:
            self.RenGouFangShi = "现金"
        return ""

    def extract(self, html_file_path):
        rs = []
        paragraphs = self.html_parser.parse_content(html_file_path)
        rs_paragraphs = self.extract_from_paragraphs(paragraphs)
        for table_dict in self.html_parser.parse_table(html_file_path):
            rs_table = self.extract_from_table_dict(table_dict)
            if len(rs_table) > 0:
                if len(rs) > 0:
                    #self.mergeRecord(rs, rs_table)
                    break
                else:
                    rs.extend(rs_table)
        # 2. 如果没有 Table Dict 则解析文本部分
        if len(rs) <= 0:
            return rs_paragraphs
        return rs

class TableDictFieldPattern(object):
    def __init__(self, field_name, convert_method, pattern, col_skip_pattern, row_skip_pattern):
        self.field_name = field_name
        self.convert_method = convert_method
        self.pattern = None
        if pattern is not None and len(pattern) > 0:
            self.pattern = re.compile(pattern)
        self.col_skip_pattern = None
        if col_skip_pattern is not None and len(col_skip_pattern) > 0:
            self.col_skip_pattern = re.compile(col_skip_pattern)
        self.row_skip_pattern = None
        if row_skip_pattern is not None and len(row_skip_pattern) > 0:
            self.row_skip_pattern = re.compile(row_skip_pattern)

    def is_match_pattern(self, text):
        if self.pattern is None:
            return False
        match = self.pattern.search(text)
        return True if match else False

    def is_match_col_skip_pattern(self, text):
        if self.col_skip_pattern is None:
            return False
        match = self.col_skip_pattern.search(text)
        return True if match else False

    def is_match_row_skip_pattern(self, text):
        if self.row_skip_pattern is None:
            return False
        match = self.row_skip_pattern.search(text)
        return True if match else False

    def get_field_name(self):
        return self.field_name

    def convert(self, text):
        if self.convert_method is None:
            return self.default_convert(text)
        elif self.convert_method == 'getStringFromText':
            return self.getStringFromText(text)
        elif self.convert_method == 'getDateFromText':
            return self.getDateFromText(text)
        elif self.convert_method == 'getLongFromText':
            return self.getLongFromText(text)
        elif self.convert_method == 'getDecimalFromText':
            return self.getDecimalFromText(text)
        elif self.convert_method == 'getDecimalRangeFromTableText':
            return self.getDecimalRangeFromTableText(text)
        else:
            return self.default_convert(text)

    @staticmethod
    def default_convert(text):
        return text

    @staticmethod
    def getStringFromText(text):
        return text

    @staticmethod
    def getDateFromText(text):
        strList = text.split("至")
        if len(strList) < 2 and ("月" in text or "年" in text or "/" in text or "." in text):
            strList = re.split("-|—|~", text)
        return strList[-1]

    @staticmethod
    def getLongFromText(text):
        return TextUtils.remove_comma_in_number(text)

    @staticmethod
    def getDecimalFromText(text):
        return text

    @staticmethod
    def getDecimalRangeFromTableText(text):
        return text