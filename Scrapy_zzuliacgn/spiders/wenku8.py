# -*- coding: utf-8 -*-
import scrapy,re,chardet,random,datetime,os.path
# from Scrapy_zzuliacgn.tools.aixinxi_tools import *
from Scrapy_zzuliacgn.customSettings import wenku8
from Scrapy_zzuliacgn.items import wenku8Item,wenku8ChapterItem

class Wenku8Spider(scrapy.Spider):
    name = "wenku8"
    allowed_domains = ["wenku8.net","wkcdn.com","httporg.bin"]
    # start_urls = ['https://www.wenku8.net/book/5.htm']
    # start_urls = ['https://www.wenku8.net/book/601.htm']
    start_urls = ['https://www.wenku8.net/book/2500.htm']

    # 控制变量
    end_check_times = 0 # 发现“出现错误”的次数
    copyrightId = [] # 发现“版权问题”的次数
    errorId = [] # 发现“文章不存在的次数”的次数

    # 正则变量
    novel_name='e:16px; font-weight: bold; line-height: 150%"><b>([\s\S]*?)</b>'  # 小说名
    novel_fromPress='<td width="20%">文库分类：([\s\S]*?)</td>'  # 文库分类
    novel_writer='<td width="20%">小说作者：([\s\S]*?)</td>'  # 作者名
    novel_intro='<span class="hottext">内容简介：</span><br /><span style="font-size:14px;">([\s\S]*?)</span>'  # 小说简介
    novel_headerImage=r'td width="20%" align="center" valign="top">\r\n          <img src="([\s\S]*?)"'  # 小说封面URL
    novel_chaImage=r'<img src="([\s\S]*?)" border="0" class="imagecontent">'  # 小说插画URL
    novel_worksNum='<td width="20%">全文长度：([\s\S]*?)字</td>'  # 小说字数
    novel_saveTime:'' # 小说收录时间
    novel_updateTime:'' # 小说更新时间
    novel_action='<td width="20%">文章状态：([\s\S]*?)</td>'  # 小说状态（连载or完结）
    index_url='<div style="text-align:center"><a href="([\s\S]*?)">小说目录</a></div>'  # 应用于某些小说网站，文章简介与文章内容分层的情况
    Chapter_title=r'<td class="vcss" colspan="4">(.*?)</td>' # 小说卷名
    Chapter_name=r'<td class="ccss"><a href="([\s\S]*?)">([\s\S]*?)</a></td>' # 小说章节名
    Chapter_img=r'<img src="([\s\S]*?)" border="0" class="imagecontent">' # 小说插图
    html_container = '\(http://www.wenku8.com\)</ul>([\s\S]*?)<ul id="contentdp">最新最全的日本动漫轻小说 轻小说文库'

    # 该爬虫所用的settings信息
    custom_settings = wenku8

    def parse(self, response):
        # 下一页
        _next = "{num}.htm".format(num=str(int(response.url[28:-4]) + 1))
        nextUrl = response.urljoin(_next)
        if response.status == 400:
            print(response.cookie)
            print(response.headers)
        if "该文章不存在" not in response.text and 'Bad Request' not in response.text:  # 不出现“出现错误”同时错误尝试次数小于5
            # print(response.text)
            main_dict = {
                '书名': self.reglux(response.text, self.novel_name, False)[0],
                '作者': self.reglux(response.text, self.novel_writer, False)[0],
                '插画师': '暂时未知',
                '文库名': self.reglux(response.text, self.novel_fromPress, False)[0],
                '简介': self.reglux(response.text, self.novel_intro, False)[0],
                '封面': self.reglux(response.text, self.novel_headerImage, False)[0],
                '全书字数': 0,# 通过web后端查找计算即可
                '类型': 14,  # 轻小说 id 14
                # '字数':self.reglux(response.text, self.novel_worksNum,False)[0],
                '文章状态': self.reglux(response.text, self.novel_action, False)[0],
                '小说目录': self.reglux(response.text, self.index_url, False)[0],
                '小说全本地址': 'http://dl.wkcdn.com/txtutf8{num}.txt'.format(num=self.reglux(response.text, self.index_url, False)[0][28:-10]),
            }
            # 版权问题小说采用全文切割法采集，否则使用html采集
            # todo ValueError: 'https://www.wenku8.net/book/2545.htm' is not in list 待解决
            self.copyrightId.append(response.url)
            if '版权问题' in response.text:
                yield scrapy.Request(url=main_dict["小说目录"], callback=self.index_info, meta={"item": main_dict,'采集方式':['full_text','html_text','chapter_text'][0]})
            else:
                yield scrapy.Request(url=main_dict["小说目录"], callback=self.index_info, meta={"item": main_dict,'采集方式':['full_text','html_text','chapter_text'][1]})
            # print('http://dl.wkcdn.com/txtgbk{num}.txt'.format(num=self.reglux(response.text, self.index_url, False)[0][28:-10]))
            yield scrapy.Request(url=main_dict["小说目录"], callback=self.index_info, meta={"item": main_dict})

            self.end_check_times = 0  # 计数初始化
            yield scrapy.Request(nextUrl, callback=self.parse)  # 跳转下一页
        else: # 出现错误
            self.end_check_times += 1  # 增加一次失败次数
            print('页面出现错误！')
            # 将被删除的id记录下来
            if self.end_check_times <= 1:
                self.errorId.append(response.url)
            if self.end_check_times <= 5:
                yield scrapy.Request(nextUrl, callback=self.parse)  # 检查下一页
            else:
                self.logFile(os.path.join('wenku8', 'wenku8Iderror.txt'), sorted(set(self.errorId[:-1]),key=self.errorId[:-1].index), 'w+', 'utf-8', True)
                print(self.copyrightId)
                self.logFile(os.path.join('wenku8', 'wenku8Copyright.txt'), sorted(set(self.copyrightId),key=self.errorId[:-1].index), 'w+', 'utf-8', True)
                print('出现错误的次数超过5次，爬虫停止！')


    def index_info(self, response):
        '''

        :param response:
        :return:
        '''
        Chapter = self.reglux(response.text, '<tr>([\s\S]*?)</tr>',False)
        main_dict = response.meta["item"]
        main_dict['小说目录'] = self.titleCuter(Chapter)
        if response.meta["采集方式"] == 'full_text':
            main_dict['小说目录'] = self.titleCuter(Chapter)
            yield scrapy.Request(url=main_dict["小说全本地址"], callback=self.full_text,meta={"item": main_dict})
        else:
            main_dict['小说目录'] = self.titleCuter(Chapter)
            for m in main_dict["小说目录"]:
                for n in main_dict["小说目录"][m]:
                    yield scrapy.Request(url=response.urljoin(n[0]), callback=self.html_text,meta={"item": main_dict,'title':m,'chapter':n,})

       # 小说基础信息
        item = wenku8Item()
        item['novelName'] = response.meta["item"]['书名']
        item['writer'] = response.meta["item"]['作者']
        item['illustrator'] = response.meta["item"]['插画师']
        item['fromPress'] = response.meta["item"]['文库名']
        item['intro'] = response.meta["item"]['简介']
        item['headerImage'] = response.meta["item"]['封面']
        item['resWorksNum'] = response.meta["item"]['全书字数']
        item['types_id'] = response.meta["item"]['类型']
        item['contents'] = str(self.index_simplify(main_dict['小说目录']))
        item['action'] = response.meta["item"]['文章状态']
        item['isdelete'] = 0
        yield item

    def html_text(self,response):
        '''
        通过html页面采集小说
        :param response:
        :return:
        '''
        print('%s %s' % (response.meta['chapter'][-1], response.url))
        # 章节插入
        item = wenku8ChapterItem()
        item['name'] = response.meta['item']['书名']
        item['title'] = response.meta['title']
        item['chapter'] = response.meta['chapter'][-1]
        item['fullName'] = '{name}_{title}_{chapter}'.format(name=response.meta['item']['书名'], title=response.meta['title'],chapter=response.meta['chapter'][-1])
        item['worksNum'] = len(self.reglux(response.text, self.html_container, False)[0].replace('<br />','').replace('&nbsp;&nbsp;&nbsp;&nbsp;','').replace('\r\n\r\n','\r\n'))
        item['updateTime'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        item['chapterImgurls'] = str([])
        item['container'] = self.reglux(response.text, self.html_container, False)[0].replace('<br />','').replace('&nbsp;&nbsp;&nbsp;&nbsp;','').replace('\r\n\r\n','\r\n')
        item['container'] = ''
        item['isdelete'] = 0

        # 判断是否存在图片
        if '暂' not in self.reglux(response.text, self.novel_chaImage, False)[0]:
            item['chapterImgurls'] = str(self.reglux(response.text, self.novel_chaImage, False))

        # 判断是否为插图章节
        if len(self.reglux(response.text, self.html_container, False)[0].replace('<br />','').split('&nbsp;&nbsp;&nbsp;&nbsp;')) == 1:
            item['container'] = ''
            item['worksNum'] = 0

        yield item


    def full_text(self,response):
        '''
        爬取全本小说，并对全本小说进行裁剪分章节
        实现思路，使用卷名和章节名称拼接正则表达式来切割小说全文本
        :param n: 遍历取对应键值中存着的列表，('2.htm', '序章 取代自我介绍的回忆—前天才美少女作家')
        :param temp_list: 获取上层请求传递的meta信息的小说目录，并将字典转列表
        :return:
        '''
        # full_text = response.body.decode(chardet.detect(response.body)['encoding']).encode('utf-8')
        if 'utf8' in response.url:
            print('utf8链接')
            full_text = response.text[35:] # 去除全本小说开头没用的信息
        else:
            print('gbk链接')
            full_text = response.body.decode('gbk')[35:] # 去除全本小说开头没用的信息

        # 字典的键和值分离成两个列表
        keys_list = list(response.meta["item"]['小说目录'])
        values_list = list(response.meta["item"]['小说目录'].values())

        tempindex = {}
        # todo 有机会可以试试用迭代器实现
        for title,chapters in zip(keys_list,values_list):
            len_chapters = len(chapters)
            tempindex[title] = []
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
                    '章节地址':'https://www.wenku8.net/novel/{}/{}'.format(response.url[27:-4],chapter[0]),
                    '更新时间':datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    '章节插画':[],
                }

                # 检查是否爬取成功
                if '暂无具体信息...' == temp_dict['正文']:
                    print('正则获取失败！尝试转换gbk全本！')
                    yield scrapy.Request(url='http://dl.wkcdn.com/txtgbk/%s'%response.url[28:], callback=self.full_text, meta={"item": response.meta['item']})

                # 放弃直接使用wenku8图片
                if temp_dict['正文'] in '\r\n\r\n\r\n\r\n' and len(temp_dict['正文']) <= 8:
                    temp_dict['章节名'] = '本册插画'
                    temp_dict['正文'] = '本册插画'

                # 章节插入
                item = wenku8ChapterItem()
                item['name'] = temp_dict['所属小说']
                item['title'] = temp_dict['卷名']
                item['chapter'] = temp_dict['章节名']
                item['fullName'] = '{name}_{title}_{chapter}'.format(name=temp_dict['所属小说'], title=temp_dict['卷名'],chapter=temp_dict['章节名'])
                item['worksNum'] = temp_dict['章节字数']
                item['updateTime'] = temp_dict['更新时间']
                item['chapterImgurls'] = str(temp_dict['章节插画'])
                item['container'] = temp_dict['正文']
                item['isdelete'] = 0
                yield item

                # 输出成文本
                # with open('%s—%s.txt' % (title,chapter[1]), 'w', encoding='utf-8') as f:
                #     f.write(self.reglux(full_text, temp_re, False)[0])

    def index_simplify(self,templist):
        '''
        将titleCuter函数的返回值简化，去除元组的url地址
        :param templist: 有元组元素的列表
        :return: 列表
        '''
        tempindex = {}
        for title, chapters in zip(list(templist), list(templist.values())):
            tempindex[title] = []
            for chapter in chapters:
                tempindex[title].append(chapter[-1])
        print(tempindex)
        return tempindex

    def logFile(self,FileName,content,model = 'a+',encod = 'utf-8',Line_break = True):
        '''
        日志打印函数，使用示例：
        self.logFile(os.path.join('wenku8','wenku8Copyright.txt'), response.url, 'a+', 'utf-8', True)
        :param FileName: 字符串，带路径和后缀的文件名
        :param content: 列表，文本内容列表
        :param model: 字符串，pythonIO操作的模式,默认a+
        :param encod: 字符串，编码格式，默认utf-8
        :param Line_break: 布尔值，是否添加换行符，默认值True
        :return:
        '''
        print(os.path.join(os.getcwd(),'log','%s'%FileName))
        with open(os.path.join(os.getcwd(),'log','%s'%FileName), '{mode}'.format(mode = model), encoding=encod) as f:
            for i in content:
                if Line_break:                    f.write(i + "\n")
                else:
                    f.write(i)

    def CheckRe(self,tempStr):
        '''
        将字符串中与正则表达式符号有冲突的符号进行转义
        :param tempStr:
        :return:
        '''
        temp = '\?$%^&.[]~{}()|<>'
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

    # 卷名识别以及章节从属（新）
    def titleCuter(self,index,ikey = 'vcss'):
        '''
        整理卷名和章节名的从属关系，采集将会按每个tr行为一个列表元素，每个列表元素中还有嵌套的元组元素
        :param index:
        :param ikey:
        :return:
        '''
        t = [] # 卷名列表
        c = [] # 章节列表
        for i in index:
            if ikey in i:
                # 发现卷名，并添加卷名到卷名列表
                t.append(self.reglux(i,self.Chapter_title,False)[0])
                # 同时在章节列表添加一个空列表元素，保持与卷名列表的下标一致
                # 章节列表中的每一个列表元素里所有元组元素，即是对应卷名列表下标的所属章节
                c.append([])
            else:
                # 章节列表末尾元素与卷名列表最新卷名元素下标一致
                c[-1] += self.reglux(i,self.Chapter_name,False)
        resdict = dict(zip(t,c))
        print(resdict)
        return resdict

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
        if len(tids) == 1:
            print('该小说未发现分多卷')
            recdict[self.reglux(tlist[0], self.Chapter_title, False)[0]] = self.reglux(''.join(tlist[1:]),self.Chapter_name, False)
        else:
            while count + 1 < len(tids):  # 使用卷名下标来对列表中属于章节的部分切片出来
                # print(tids[count])
                # print(tids[count+1])
                # print(tlist[tids[count]:tids[count + 1]])
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