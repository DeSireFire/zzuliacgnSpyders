# -*- coding: utf-8 -*-
import scrapy


class Wenku8netSpider(scrapy.Spider):
    name = "wenku8Net"
    allowed_domains = ["wenku8.net", "wkcdn.com"]
    start_urls = ['https://www.wenku8.net/book/2.htm']

    # xpath 字典
    xpathDict = {
        'novelName':"//table[1]//span//b/text()",
        'headerImage':"//td//img[@vspace='0']/@src",
        'fromPress':"//div[@id='content']/div[1]//tr[2]/td[1]/text()",
        'writer':"//div[@id='content']/div[1]//tr[2]/td[2]/text()",
        'action':"//div[@id='content']/div[1]//tr[2]/td[3]/text()",
        '最后更新':"//div[@id='content']/div[1]//tr[2]/td[4]/text()",
        'resWorksNum':"//div[@id='content']/div[1]//tr[2]/td[5]/text()",
    }
    # 正则字典
    reDict = {
        'intro': '<span class="hottext">内容简介：</span><br /><span style="font-size:14px;">([\s\S]*?)</span>',
    }
    def parse(self, response):
        # firstDict = {
        #     '书名':self.xpathHandler(response,self.xpathDict['书名'])[0],
        #     '封面':self.xpathHandler(response,self.xpathDict['封面'])[0],
        #     '文库分类':self.xpathHandler(response,self.xpathDict['文库分类'])[0][5:],
        #     '作者名':self.xpathHandler(response,self.xpathDict['作者名'])[0][5:],
        #     '文章状态':self.xpathHandler(response,self.xpathDict['文章状态'])[0][5:],
        #     '最后更新':self.xpathHandler(response,self.xpathDict['最后更新'])[0][5:],
        #     '全文字数':self.xpathHandler(response,self.xpathDict['全文字数'])[0][5:],
        #     # '简介':max(self.xpathHandler(response,self.xpathDict['简介']), key=len),
        #     '简介':self.reglux(response.text,self.reDict['简介'],False)[0],
        # }

        firstDict = {
            'illustrator': '',
            'types_id': '',
            'contents': '',
            'isdelete': 0,
        }

        print(firstDict)

    def xpathHandler(self,response,xpathStr):
        '''
        xpath 处理函数
        :param response:
        :param xpathStr:
        :return:
        '''
        temp = response.xpath(xpathStr).extract()
        if temp:
            return temp
        else:
            return ['暂无数据']

    def reglux(self, html_text, re_pattern, nbsp_del=True):
        '''
        正则过滤函数
        :param html_text: 字符串，网页的文本
        :param re_pattern: 字符串，正则表达式
        :param nbsp_del: 布尔值，控制是否以去除换行符的形式抓取有用信息
        :return:
        '''
        import re
        # re_pattern = re_pattern.replace('~[',"\~\[").replace(']~','\]\~')
        pattern = re.compile(re_pattern)
        if nbsp_del:
            temp = pattern.findall("".join(html_text.split()))
        else:
            temp = pattern.findall(html_text)
        if temp:
            return temp
        else:
            return ['暂无具体信息...']

if __name__ == '__main__':
    from scrapy import cmdline
    cmdline.execute(['scrapy', 'crawl', 'wenku8Net'])