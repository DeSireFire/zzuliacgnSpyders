# -*- coding: utf-8 -*-
import scrapy,re,chardet,random


class Wenku8Spider(scrapy.Spider):
    name = "wenku8"
    allowed_domains = ["wenku8.net","wkcdn.com","httporg.bin"]
    start_urls = ['https://www.wenku8.net/book/1.htm']

    novel_name='e:16px; font-weight: bold; line-height: 150%"><b>([\s\S]*?)</b>'  # 小说名
    novel_writer='<td width="20%">小说作者：([\s\S]*?)</td>'  # 作者名
    novel_intro='<span class="hottext">内容简介：</span><br /><span style="font-size:14px;">([\s\S]*?)</span>'  # 小说简介
    novel_headerImage=r'td width="20%" align="center" valign="top">\r\n          <img src="([\s\S]*?)"'  # 小说封面URL
    novel_worksNum='<td width="20%">全文长度：([\s\S]*?)</td>'  # 小说字数
    novel_saveTime:'' # 小说收录时间
    novel_updateTime:'' # 小说更新时间
    novel_action='<td width="20%">文章状态：([\s\S]*?)</td>'  # 小说状态（连载or完结）
    index_url='<div style="text-align:center"><a href="([\s\S]*?)">小说目录</a></div>'  # 应用于某些小说网站，文章简介与文章内容分层的情况
    Chapter_title=r'<td class="vcss" colspan="4">(.*?)</td>' # 小说卷名
    Chapter_name=r'<td class="ccss"><a href="([\s\S]*?)">([\s\S]*?)</a></td>' # 小说章节名
    # def start_requests(self):
    #     url = 'https://www.wenku8.net/book/{num}.htm'
    #     for i in range(1, 51):
    #         yield scrapy.Request(url.format(i), callback=self.parse)

    def parse(self, response):
        main_dict = {
            '书名':self.reglux(response.text, self.novel_name,False)[0],
            '作者':self.reglux(response.text, self.novel_writer,False)[0],
            '简介':self.reglux(response.text, self.novel_intro,False)[0],
            '封面':self.reglux(response.text, self.novel_headerImage,False)[0],
            '字数':self.reglux(response.text, self.novel_worksNum,False)[0],
            '文章状态':self.reglux(response.text, self.novel_action,False)[0],
            '小说目录地址':self.reglux(response.text, self.index_url,False)[0],
            '小说全本地址':'http://dl.wkcdn.com/txtutf8{num}.txt'.format(num = self.reglux(response.text, self.index_url,False)[0][28:-10]),
        }
        print(main_dict)
        yield scrapy.Request(url=main_dict["小说目录地址"], callback=self.index_info, meta={"item": main_dict})

    def index_info(self, response):

        Chapter = self.reglux(response.text, '<tr>([\s\S]*?)</tr>',False)
        recdict = self.titleCheck(Chapter)
        for i in recdict:
            print('%s:%s'%(i,recdict[i]))

    def reglux(self, html_text, re_pattern, nbsp_del=True):
        '''
        正则过滤函数
        :param html_text: 字符串，网页的文本
        :param re_pattern: 字符串，正则表达式
        :param nbsp_del: 布尔值，控制是否以去除换行符的形式抓取有用信息
        :return:
        '''
        pattern = re.compile(re_pattern)
        if nbsp_del:
            temp = pattern.findall("".join(html_text.split()))
        else:
            temp = pattern.findall(html_text)
        if temp:
            return temp
        else:
            return '暂无具体信息...'

    # 卷名识别以及章节从属
    def titleCheck(self, tlist, tkey='class="vcss"'):
        """
        若出现卷名和章节名都在同一个页面时（例如：https://www.wenku8.net/novel/1/1592/index.htm）,
        用此函数整理分卷和其所属章节的关系,并用reglux_list方法进行清洗
        :param tlist:列表，包含卷名和章节名的列表
        :param tkey:字符串，用来判断区分列表卷名和章节的关键字
        :return:recdict
        """
        tids = []  # 筛选出“原矿”列表中，所有册名的下标
        for i in tlist:
            if tkey in i:
                tids.append(tlist.index(i))
        count = 0
        recdict = {}
        while count + 1 < len(tids):  # 使用卷名下标来对列表中属于章节的部分切片出来
            temp = tlist[tids[count]:tids[count + 1]]
            if count + 1 == len(tids) - 1:
                temp = tlist[tids[count + 1]:]
                '''
                temp[0]必包含卷名，其后temp[1:]均为其所属章节名
                temp[0] 取出带有卷名未清洗的html，例如：<td class="vcss" colspan="4">短篇</td>；
                self.reglux(temp[0],self.Chapter_title,False 通过正则得到列表，下标0的位置为清洗出的卷名,例如：短篇；
                self.reglux(''.join(temp[1:]),self.Chapter_name,False) 通过正则清洗，得到章节地址和章节名；
                recdict为字典，recdict[key]=value,给键赋值；
                '''
            recdict[ self.reglux(temp[0],self.Chapter_title,False)[0] ] = self.reglux(''.join(temp[1:]),self.Chapter_name,False)
            count += 1
        return recdict
    # def reglux_list(self,mydict, responseSTR):
    #     """
    #     遍历正则抓取数据
    #     :param mydict: 字典类型{key:正则表达式，}
    #     :param responseSTR: request.text需要正则匹配的字符串
    #     :return: 字典类型
    #     """
    #     temp = {}
    #     for m, n in mydict.items():
    #         if '' != n:
    #             pattern = re.compile(n)
    #             matchs = pattern.findall(responseSTR)
    #             temp.update({m: matchs, })
    #         else:
    #             temp.update({m: list(n), })
    #     return temp