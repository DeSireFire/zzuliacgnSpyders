# -*- coding: utf-8 -*-
import scrapy,random


class Wenku8netSpider(scrapy.Spider):
    name = "wenku8Net"
    allowed_domains = ["wenku8.net", "wkcdn.com"]
    # start_urls = ['https://www.wenku8.net/book/1.htm']
    start_urls = ['https://www.wenku8.net/book/%s.htm'%random.randint(1,2589)]

    # xpath 字典
    xpathDict = {
        'novelName':"//table[1]//span//b/text()",
        'headerImage':"//td//img[@vspace='0']/@src",
        'updateTime': "//div[@id='content']/div[1]//tr[2]/td[4]/text()",
        'resWorksNum':"//div[@id='content']/div[1]//tr[2]/td[5]/text()",
    }
    xpathDict2 = {
        '章节':"//tr/td",
        '章节名':"//tr/td/a/text()",
        '章节url':"//tr/td/a/@href",
    }
    # 正则 字典
    reDict = {
        'fromPress': '<td width="20%">文库分类：([\s\S]*?)</td>',
        'writer': '<td width="20%">小说作者：([\s\S]*?)</td>',
        'action': '<td width="20%">文章状态：([\s\S]*?)</td>',
        'intro': '<span class="hottext">内容简介：</span><br /><span style="font-size:14px;">([\s\S]*?)</span>',
    }
    def parse(self, response):
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

        metaDict = {
            'copyRight':False, # 是否存在版权问题
            'urlDict':urlDict, # 用到的URL
            'info':firstDict,   # 小说信息
            'indexT':[],   # 卷名
            'indexC':[],   # 章节名
        }

        if '版权问题' in response.text:
            metaDict['copyRight'] = True

        # 判断是否正确获取小说信息
        if firstDict['novelName'] != '暂时未知':
            yield scrapy.Request(url=urlDict['小说目录'], callback=self.directory,meta=metaDict) # 加载目录页

        # 加载下一页
        # _nextPage = self.nextPages(response)
        # if _nextPage:
        #     yield scrapy.Request(url= _nextPage, callback=self.parse)

    def directory(self,response):
        t = [] # 卷名列表
        c = [] # 章节列表
        for i in [i for i in self.xpathHandler(response,self.xpathDict2['章节']) if '<td class="ccss">\xa0</td>' not in i]:
            if 'vcss' in i :
                t.append(i[29:-5])
                c.append([])
            else:
                temp = [i[26:-9].split('">')]
                temp[0][0] = response.url.replace('index.htm',temp[0][0])
                c[-1] += temp

        metaDict = response.meta
        metaDict['indexT'] = t
        metaDict['indexC'] = c

        import chardet
        jsonDict = {}
        for m,n in zip(t,c):
            jsonDict[m] = []
            for x in n:
                jsonDict[m].append({x[1]:x[0]})
        print(jsonDict)

        import json
        print(str(jsonDict).replace("'",'"'))
        print(json.loads(str(jsonDict).replace("'",'"')))
        # print(json.dumps(jsonDict).encode('utf8'))
        # print(type(json.dumps(jsonDict)))
        # print(json.loads(json.dumps(jsonDict)))



        # 根据版权下架选择采集方式
        if response.meta['copyRight']:
            print('直接爬取')
            for m,n in zip(t,c):
                print(m,n)
        else:
            print('No')

    def test(self,response):
        temp = [i for i in response.text.split('\r\n') if i != '']
        print(len(temp))
        for i in range(1,10):
            print([temp[i]])
        temp = [i for i in response.text.split('\r\n') if i != '' or '    <td class="ccss">&nbsp;</td>' not in i]
        print(len(temp))
        for i in temp[59:-25]:
            print([i])


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