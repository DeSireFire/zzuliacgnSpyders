# -*- coding: utf-8 -*-
import scrapy


class Wenku8netSpider(scrapy.Spider):
    name = "wenku8Net"
    allowed_domains = ["wenku8.net", "wkcdn.com"]
    start_urls = ['https://www.wenku8.net/book/256.htm']

    # xpath 字典
    xpathDict = {
        'novelName':"//table[1]//span//b/text()",
        'headerImage':"//td//img[@vspace='0']/@src",
        'updateTime': "//div[@id='content']/div[1]//tr[2]/td[4]/text()",
        'resWorksNum':"//div[@id='content']/div[1]//tr[2]/td[5]/text()",
    }
    # 正则 字典
    reDict = {
        'fromPress': '<td width="20%">文库分类：([\s\S]*?)</td>',
        'writer': '<td width="20%">小说作者：([\s\S]*?)</td>',
        'action': '<td width="20%">文章状态：([\s\S]*?)</td>',
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
            'types_id': 14,
            'contents': '',
            'isdelete': 0,
            'illustrator': '暂时未知',
        }
        for m,n in self.xpathDict.items():
            firstDict[m] = self.xpathHandler(response,n)[0]
        for m,n in self.reDict.items():
            firstDict[m] = self.reglux(response.text,n,False)[0]

        novelId = int(response.url[28:-4])
        urlDict = {
            '小说目录':'https://www.wenku8.net/novel/{num}/{id}/index.htm'.format(
                num = str((novelId + 1)//1000),
                id = str(novelId)),
            '小说全本':'http://dl.wenku8.com/down.php?type=utf8&id={id}'.format(id = novelId),

        }

        # 判断是否正确获取小说信息
        if firstDict['novelName'] != '暂时未知':
            yield scrapy.Request(url=urlDict['小说目录'], callback=self.directory) # 加载目录页

        # 加载下一页
        _nextPage = self.nextPages(response)
        if _nextPage:
            yield scrapy.Request(url= _nextPage, callback=self.parse)

    def directory(self,response):
        temp = [i for i in response.text.split('\r\n') if i != '']
        print(len(temp))
        for i in temp[47:-19]:
            print([i])

    def test(self,response):
        temp = [i for i in response.text.split('\r\n') if i != '']
        print(len(temp))
        for i in range(1,10):
            print([temp[i]])


    def nextPages(self,response):
        '''
        翻页函数
        :param checkUrl:布尔值，检查后几页是否也为 “文章不存在”
        :return:
        '''
        urlStr = 'https://www.wenku8.net/book/%s.htm'%str(int(response.url[28:-4]) + 1)
        # print('666')
        if int(response.url[28:-4]) + 1 < 2590:
            return urlStr
        else:
            return None

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
            return ['暂无数据']

if __name__ == '__main__':
    from scrapy import cmdline
    cmdline.execute(['scrapy', 'crawl', 'wenku8Net'])