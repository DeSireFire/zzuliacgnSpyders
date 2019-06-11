# -*- coding: utf-8 -*-
import scrapy


class Wenku8netSpider(scrapy.Spider):
    name = "wenku8Net"
    allowed_domains = ["wenku8.net", "wkcdn.com"]
    start_urls = ['https://www.wenku8.net/book/5000.htm']

    # xpath 字典
    wName = "//table[1]//span//b/text()",
    wInfo = "//body//div[@id='centerl']/div[@id='content']/div[1]/table[1]//tr[2]/td/text()",
    def parse(self, response):
        print(response.text)
        temp = response.xpath(self.wName).extract()
        print(temp)

if __name__ == '__main__':
    from scrapy import cmdline
    cmdline.execute(['scrapy', 'crawl', 'wenku8Net'])