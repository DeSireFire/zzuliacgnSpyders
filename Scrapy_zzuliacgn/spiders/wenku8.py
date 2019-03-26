# -*- coding: utf-8 -*-
import scrapy,re,chardet,random,datetime
# from Scrapy_zzuliacgn.tools.aixinxi_tools import *
from Scrapy_zzuliacgn.customSettings import wenku8
# from Scrapy_zzuliacgn.items import wenku8Item

class Wenku8Spider(scrapy.Spider):
    name = "wenku8"
    allowed_domains = ["wenku8.net","wkcdn.com","httporg.bin"]
    start_urls = ['https://www.wenku8.net/book/1.htm']

    novel_name='e:16px; font-weight: bold; line-height: 150%"><b>([\s\S]*?)</b>'  # 小说名
    novel_fromPress='<td width="20%">文库分类：([\s\S]*?)</td>'  # 文库分类
    novel_writer='<td width="20%">小说作者：([\s\S]*?)</td>'  # 作者名
    novel_intro='<span class="hottext">内容简介：</span><br /><span style="font-size:14px;">([\s\S]*?)</span>'  # 小说简介
    novel_headerImage=r'td width="20%" align="center" valign="top">\r\n          <img src="([\s\S]*?)"'  # 小说封面URL
    novel_worksNum='<td width="20%">全文长度：([\s\S]*?)字</td>'  # 小说字数
    novel_saveTime:'' # 小说收录时间
    novel_updateTime:'' # 小说更新时间
    novel_action='<td width="20%">文章状态：([\s\S]*?)</td>'  # 小说状态（连载or完结）
    index_url='<div style="text-align:center"><a href="([\s\S]*?)">小说目录</a></div>'  # 应用于某些小说网站，文章简介与文章内容分层的情况
    Chapter_title=r'<td class="vcss" colspan="4">(.*?)</td>' # 小说卷名
    Chapter_name=r'<td class="ccss"><a href="([\s\S]*?)">([\s\S]*?)</a></td>' # 小说章节名
    Chapter_img=r'<img src="([\s\S]*?)" border="0" class="imagecontent">' # 小说插图

    # 该爬虫所用的settings信息
    custom_settings = wenku8

    # 检测custom_settings中爱信息图床的头部是否可用
    # if not logining(aixinxi_header):
    #     print('爱信息图床登陆状态不正常！')
    #     aixinxi_header = login()
    #     print(aixinxi_header)
    # else:
    #     print('爱信息图床登陆状态正常！')
    # def start_requests(self):
    #     url = 'https://www.wenku8.net/book/{num}.htm'
    #     for i in range(1, 2):
    #         yield scrapy.Request(url.format(i), callback=self.parse)

    def parse(self, response):
        main_dict = {
            '书名':self.reglux(response.text, self.novel_name,False)[0],
            '作者':self.reglux(response.text, self.novel_writer,False)[0],
            '文库名':self.reglux(response.text, self.novel_fromPress,False)[0],
            '简介':self.reglux(response.text, self.novel_intro,False)[0],
            '封面':self.reglux(response.text, self.novel_headerImage,False)[0],
            '全书字数':0,
            '类型':'轻小说',
            # '字数':self.reglux(response.text, self.novel_worksNum,False)[0],
            '文章状态':self.reglux(response.text, self.novel_action,False)[0],
            '小说目录':self.reglux(response.text, self.index_url,False)[0],
            '小说全本地址':'http://dl.wkcdn.com/txtutf8{num}.txt'.format(num = self.reglux(response.text, self.index_url,False)[0][28:-10]),
        }
        print(main_dict)
        yield scrapy.Request(url=main_dict["小说目录"], callback=self.index_info, meta={"item": main_dict})

    def index_info(self, response):
        '''

        :param response:
        :return:
        '''
        Chapter = self.reglux(response.text, '<tr>([\s\S]*?)</tr>',False)
        main_dict = response.meta["item"]
        main_dict['小说目录'] = self.titleCheck(Chapter)
        # for i in response.meta["item"]['小说目录']:
        #     print('%s:%s'%(i,response.meta["item"]['小说目录'][i]))

        yield scrapy.Request(url=main_dict["小说全本地址"], callback=self.full_text,meta={"item": main_dict})



    def full_text(self,response):
        '''
        爬取全本小说，并对全本小说进行裁剪分章节

        实现思路，使用卷名和章节名称拼接正则表达式来切割小说全文本
        :param n: 遍历取对应键值中存着的列表，('2.htm', '序章 取代自我介绍的回忆—前天才美少女作家')
        :param temp_list: 获取上层请求传递的meta信息的小说目录，并将字典转列表
        :return:
        '''
        full_text = response.text[35:] # 去除全本小说开头没用的信息

        # 字典的键和值分离成两个列表
        keys_list = list(response.meta["item"]['小说目录'])
        values_list = list(response.meta["item"]['小说目录'].values())

        res_list = []
        # todo 有机会可以试试用迭代器实现
        for title,chapters in zip(keys_list,values_list):
            len_chapters = len(chapters)
            for chapter in chapters:
                if len_chapters != chapters.index(chapter) + 1:  # 判断是否不为章节列表最后一个元素
                    temp_re = "{title} {chapter}([\s\S]*?){next_title} {next_chapter}".format(title=self.CheckRe(title), chapter=self.CheckRe(chapter[1]), next_title=self.CheckRe(title), next_chapter=self.CheckRe(chapters[chapters.index(chapter)+1][1]))  # 拼接正则表达式,"卷名 章节名([\s\S]*?)卷名/下一卷名 下一章节 "
                else:  # 判断为章节列表最后一个元素，获取下一卷/册的第一个章节名
                    if chapter == values_list[-1][-1]: # 最后一个列表的最后一个元组，判断是否为本书的最后一个章节
                        # 是，则拼接最末尾的特殊字符串来完成正则表达式
                        temp_re = "{title} {chapter}([\s\S]*?){end}".format(title=self.CheckRe(title), chapter=self.CheckRe(chapter[1]), end='◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆')  # 拼接正则表达式,"卷名 章节名([\s\S]*?)卷名/下一卷名 下一章节 "
                    else:
                        temp_re = "{title} {chapter}([\s\S]*?){next_title} {next_chapter}".format(title=self.CheckRe(title), chapter=self.CheckRe(chapter[1]), next_title=self.CheckRe(keys_list[keys_list.index(title)+1]), next_chapter=self.CheckRe(response.meta["item"]['小说目录'][keys_list[keys_list.index(title)+1]][0][1]))  # 拼接正则表达式,"卷名 章节名([\s\S]*?)卷名/下一卷名 下一章节 "

                temp_dict = {
                    '正文': self.reglux(full_text, temp_re, False)[0],
                    '正则表达式': temp_re,
                    '卷名':title,
                    '章节名':chapter[1],
                    '所属小说':response.meta["item"]['书名'],
                    '章节地址':'https://www.wenku8.net/novel{}/{}'.format(response.url[27:-4],chapter[0]),
                    '更新时间':datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    '章节插画':[],
                }

                # 字数统计
                temp_dict['章节字数'] = len(''.join(temp_dict['正文']))
                response.meta["item"]['全书字数'] += temp_dict['章节字数']

                # 放弃直接使用wenku8图片
                if temp_dict['正文'] == '\r\n\r\n\r\n\r\n':
                    temp_dict['章节名'] = '本册插画'
                    temp_dict['正文'] = '本册插画'
                res_list.append(temp_dict)

                # 精简一下小说目录

                # 输出成文本
                # with open('%s—%s.txt' % (title,chapter[1]), 'w', encoding='utf-8') as f:
                #     f.write(self.reglux(full_text, temp_re, False)[0])

        # todo 这一步已经可以整理入库了
        print(response.meta["item"])
        end_dict = response.meta["item"]
        end_dict['小说目录'] = res_list


    def CheckRe(self,tempStr):
        '''
        将字符串中与正则表达式符号有冲突的符号进行转义
        :param tempStr:
        :return:
        '''
        temp = '\?$%^&.[]~{}()|'
        for i in temp:
            tempStr = tempStr.replace(i,'\%s'%i)
        return tempStr

    def reglux(self, html_text, re_pattern, nbsp_del=True):
        '''
        正则过滤函数
        :param html_text: 字符串，网页的文本
        :param re_pattern: 字符串，正则表达式
        :param nbsp_del: 布尔值，控制是否以去除换行符的形式抓取有用信息
        :return:
        '''
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