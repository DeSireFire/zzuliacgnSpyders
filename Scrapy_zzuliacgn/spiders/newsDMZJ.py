# -*- coding: utf-8 -*-
import scrapy


class NewsdmzjSpider(scrapy.Spider):
    name = "newsDMZJ"
    allowed_domains = ["dmzj.com"]
    start_urls = ['http://dmzj.com/']

    def parse(self, response):
        pass
