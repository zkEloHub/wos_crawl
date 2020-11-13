# encoding: utf-8
from scrapy import cmdline

def crawl_by_query(query, output_path='../output', document_type='Article', output_format='tabWinUTF8', send_url = "", txt_prename = ""):
    cmdline.execute(
        r'scrapy crawl post_craw -a output_path={} -a output_format={}'.format(output_path, output_format).split() + ['-a', 'query={}'.format(query), '-a', 'document_type={}'.format(document_type), '-a', 'send_url={}'.format(send_url), '-a', 'txt_prename={}'.format(txt_prename)])

if __name__ == '__main__':
    # 无界面下载
    url = input("输入要爬取网站链接: ")
    # txt文件开头名称
    prename = input("输入存储文件开头名称: ")
    crawl_by_query(query='CU=USA', output_path='../2019', document_type='Article', output_format='tabWinUTF8', send_url = url, txt_prename = prename)