# -*- coding: utf-8 -*-
import scrapy
# 测试用爬虫，用于查看传参结果

# FormRequest 方法用于用于发送带参数请求
from scrapy.http import FormRequest

class HttpbinSpider(scrapy.Spider):
    name = "httpbin"
    allowed_domains = ["httpbin.org"]
    start_urls = ['http://httpbin.org/get']

    def start_requests(self):
        self.start_urls[0] = str(input("输入爬取的网址:"))
        yield scrapy.Request( self.start_urls[0], callback=self.parse)

    def parse(self, response):
        self.logger.debug(response.text)
