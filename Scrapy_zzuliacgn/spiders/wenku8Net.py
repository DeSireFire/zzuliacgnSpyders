# -*- coding: utf-8 -*-
import scrapy


class Wenku8netSpider(scrapy.Spider):
    name = "wenku8Net"
    allowed_domains = ["wenku8.net", "wkcdn.com"]
    start_urls = ['https://www.wenku8.net/book/5000.htm']

    # xpath 字典
    xpathDict = {
        '书名':"//table[1]//span//b/text()",
        '封面':"//td//img[@vspace='0']/@src",
        '文库分类':"//div[@id='content']/div[1]//tr[2]/td[1]/text()",
        '作者名':"//div[@id='content']/div[1]//tr[2]/td[2]/text()",
        '文章状态':"//div[@id='content']/div[1]//tr[2]/td[3]/text()",
        '最后更新':"//div[@id='content']/div[1]//tr[2]/td[4]/text()",
        '全文字数':"//div[@id='content']/div[1]//tr[2]/td[5]/text()",
        '简介':"//span[5]/text()",
    }
    def parse(self, response):
        firstDict = {
            '书名':"//table[1]//span//b/text()",
            '封面':"//td//img[@vspace='0']/@src",
            '文库分类':"//div[@id='content']/div[1]//tr[2]/td[1]/text()",
            '作者名':"//div[@id='content']/div[1]//tr[2]/td[2]/text()",
            '文章状态':"//div[@id='content']/div[1]//tr[2]/td[3]/text()",
            '最后更新':"//div[@id='content']/div[1]//tr[2]/td[4]/text()",
            '全文字数':"//div[@id='content']/div[1]//tr[2]/td[5]/text()",
            '简介':"//span[5]/text()",
        }
        for k,v in self.xpathDict.items():
            firstDict[k] = self.xpathHandler(response,v)
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
            return temp[0]
        else:
            return ['暂无数据'][0]

if __name__ == '__main__':
    from scrapy import cmdline
    cmdline.execute(['scrapy', 'crawl', 'wenku8Net'])