# -*- coding: utf-8 -*-
import scrapy
import re
import requests
from scrapy.http import Request
from scrapy.http import FormRequest
import time
from bs4 import BeautifulSoup
import os
import sys


class PostCrawSpider(scrapy.Spider):
    name = 'post_craw'
    allowed_domains = ['apps.webofknowledge.com']

    # 提取URL中SID和QID的正则表达式
    sid_pattern = r'SID=(\w+)&'
    qid_pattern = r'qid=(\d+)&'

    start_urls = []
    
    SID = ''
    qid = ''

    # 其他必要参数设置以及初始化
    document_type = 'Article'
    output_format = 'tabWinUTF8'
    output_path = '../Data'
    query = None
    txt_prename = ''

    def __init__(self,query = None,output_path = '../Data',document_type = 'Article',output_format = 'tabWinUTF8',send_url = None,txt_prename = None,gui = None,*args, **kwargs):
        super().__init__(*args, **kwargs)
        self.query = query
        self.output_path = output_path
        self.document_type = document_type
        self.output_format = output_format
        self.gui = gui
        self.txt_prename = txt_prename
        self.start_urls.append(send_url)
        # self.start_urls.append(send_url)
        # 记录已下载数，传给gui
        self.downloaded = 0
        
        # self.url = send_url
        print('crawler 中的url为: ',send_url)

        pattern = re.compile(self.sid_pattern)  # 生成一个正则表达式对象，供match()和search()使用
        result = re.search(pattern,send_url)
        if result is not None:
            self.SID = result.group(1)
            print('提取到的SID为: ',self.SID)
        else:
            print('SID 提取失败,请检查url是否正确')
            self.SID = None

        pattern = re.compile(self.qid_pattern) # 生成正则表达式对象
        result = re.search(pattern,send_url)
        if result is not None:
            self.qid = result.group(1)
            print('提取到的qid为: ',self.qid)
        else:
            print('qid提取失败,请检查url是否正确')
            self.qid = None

        if query is None:
            print('请指定检索式!')
        if output_path is None:
            print('请指定输出路径!')

        print('文件输出路径：',output_path)
        print('检索式:',query)

    # def start_requests(self):
    #     print('开始执行')
    #     yield Request(url = self.url, dont_filter = True, method = 'GET', callback = self.parse)


    def parse(self, response):
        print('parse函数开始执行')

        # 通过bs4获取页面结果数字，得到需要分批爬取的批次数
        soup = BeautifulSoup(response.text,'lxml')
        paper_num = int(soup.find('span',attrs={'id':'footer_formatted_count'}).get_text().replace(',',''))
        span = 500
        iter_num = paper_num // span + 1
        # 获取总条数，并分成每份 500 条发送
        self.time_start = time.time()
        print('共有{}条文献需要下载.'.format(paper_num))
        for i in range(1,iter_num + 1):
            end = i * span
            start = (i - 1) * span + 1
            if end > paper_num:
                end = paper_num
            print('正在下载第{} 到第{} 条文献.'.format(start,end))
            post_form = {
                "selectedIds": "",
                "displayCitedRefs": "true",
                "displayTimesCited": "true",
                "displayUsageInfo": "true",
                "viewType": "summary",
                "product": "WOS",
                "rurl": response.url,
                "mark_id": "WOS",
                "colName": "WOS",
                "search_mode": "AdvancedSearch",
                "locale": "en_US",
                "view_name": "WOS-summary",
                "sortBy": "PY.D;LD.D;SO.A;VL.D;PG.A;AU.A",
                "mode": "OpenOutputService",
                "qid": self.qid,
                "SID": self.SID,
                "format": "saveToFile",
                "filters": "HIGHLY_CITED HOT_PAPER OPEN_ACCESS PMID USAGEIND AUTHORSIDENTIFIERS ACCESSION_NUM FUNDING SUBJECT_CATEGORY JCR_CATEGORY LANG IDS PAGEC SABBR CITREFC ISSN PUBINFO KEYWORDS CITTIMES ADDRS CONFERENCE_SPONSORS DOCTYPE CITREF ABSTRACT CONFERENCE_INFO SOURCE TITLE AUTHORS  ",
                "mark_to": str(end),
                "mark_from": str(start),
                "queryNatural": str(self.query),
                "count_new_items_marked": "0",
                "use_two_ets": "false",
                "IncitesEntitled": "yes",    # yes???
                "value(record_select_type)": "range",
                "markFrom": str(start),
                "markTo": str(end),
                "fields_selection": "HIGHLY_CITED HOT_PAPER OPEN_ACCESS PMID USAGEIND AUTHORSIDENTIFIERS ACCESSION_NUM FUNDING SUBJECT_CATEGORY JCR_CATEGORY LANG IDS PAGEC SABBR CITREFC ISSN PUBINFO KEYWORDS CITTIMES ADDRS CONFERENCE_SPONSORS DOCTYPE CITREF ABSTRACT CONFERENCE_INFO SOURCE TITLE AUTHORS  ",
                "save_options": self.output_format
            }

            # 将下载地址yield一个FormRequest给download_file函数, mete 可传递有用参数
            output_url = 'http://apps.webofknowledge.com/OutboundService.do?action=go&&'
            yield FormRequest(output_url, method = 'POST', formdata = post_form, dont_filter = True, callback = self.download_file, errback = self.err_handle , meta = {'start': start, 'end': end, 'paper_num': paper_num})
            # dont_filter 当需要多次提交表单，且url一样时，需要添加该参数
    # 异常处理
    def err_handle(self,response):
        start = response.meta['start']
        end = response.meta['end']
        print('下载文件第{} 条到第{} 条失败!!!!'.format(start,end))

    def download_file(self,response):
        file_postfix = 'txt'
        start = response.meta['start']
        end = response.meta['end']
        paper_num = response.meta['paper_num']

        filename = self.output_path + '/{}.{}'.format(self.txt_prename + str(start) + '-' + str(end),file_postfix)
        os.makedirs(os.path.dirname(filename), exist_ok = True)
        text = response.text
        # response.text 即为下载的文献

        with open(filename, 'w', encoding = 'utf-8') as file:
            file.write(text)

        print('----下载第{} 到第{} 条文献成功！！----'.format(start,end))

        # 更新进度条
        self.downloaded += end - start + 1
        print(self.downloaded/paper_num * 100)
        if self.gui is not None:
            self.gui.pbar.setValue(self.downloaded/paper_num * 100)

    def close(self, spider, reason):
        print('所有数据下载完成!!')