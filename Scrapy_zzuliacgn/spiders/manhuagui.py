# -*- coding: utf-8 -*-
import scrapy


class ManhuaguiSpider(scrapy.Spider):
    name = "manhuagui"
    allowed_domains = ["manhuagui.com"]
    start_urls = ['http://manhuagui.com/']

    def parse(self, response):
        pass
