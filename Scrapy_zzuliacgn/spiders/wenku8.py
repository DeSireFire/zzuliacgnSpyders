# -*- coding: utf-8 -*-
import scrapy,re,chardet,random,datetime


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
            '小说目录':self.reglux(response.text, self.index_url,False)[0],
            '小说全本地址':'http://dl.wkcdn.com/txtutf8{num}.txt'.format(num = self.reglux(response.text, self.index_url,False)[0][28:-10]),
        }
        print(main_dict)
        yield scrapy.Request(url=main_dict["小说目录"], callback=self.index_info, meta={"item": main_dict})

    def index_info(self, response):
        Chapter = self.reglux(response.text, '<tr>([\s\S]*?)</tr>',False)
        main_dict = response.meta["item"]
        main_dict['小说目录'] = self.titleCheck(Chapter)
        # for i in response.meta["item"]['小说目录']:
        #     print('%s:%s'%(i,response.meta["item"]['小说目录'][i]))
        yield scrapy.Request(url=main_dict["小说全本地址"], callback=self.full_text,meta={"item": main_dict})

    def full_text(self,response):
        main_dict = response.meta["item"]
        full_text = response.text[35:]
        # print([full_text])

        index_list = []
        # todo 两处大循环需要合并
        for m in main_dict['小说目录']:
            # main_dict['小说目录'] : 第一卷 渴望死亡的小丑:[('2.htm', '序章 取代自我介绍的回忆—前天才美少女作家'), ('3.htm', '第一章 远子学姐是美食家'), ('4.htm', '第二章 这个世界上最美味的故事'), ('5.htm', '第三章 第一手记--片冈愁二的告白'), ('6.htm', '第四章 五月放晴天，他
            # ……'), ('7.htm', '第五章 『文学少女』的推理'), ('8.htm', '第六章 『文学少女』的主张'), ('9.htm', '终章 新的故事'), ('10.htm', '后记'), ('24315.htm', '插图')]
            # m 为取 字典中的键
            for n in main_dict['小说目录'][m]:
            # n 遍历取对应键值中存着的列表
            # n :('2.htm', '序章 取代自我介绍的回忆—前天才美少女作家')

            #     print('%s %s([\s\S]*?)'%(m,n[1]))

            # 将拼接好的字符串存入列表
                index_list.append('%s %s'%(m,n[1]))
        # 添加一个没什么卵用的列表末尾元素，方便生成正则表达式，
        index_list.append('◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆')
        # index_list = list(set(index_list))
        print(index_list)
        # 临时存储列表
        temp = []
        for m in main_dict['小说目录']:
            # print('当前卷名：%s' % m)
            # todo 此处全遍历过于消耗性能
            index_len_count = 0
            for n in index_list[:-1]:# 舍弃上面的没用的末尾元素，避免出现超出列表下标范围
                if m in n:
                    # print('章节:< %s >属于《 %s 》'%(n,m))
                    # # 通过表达式获取章节里面的小说内容
                    res_re = ('%s([\s\S]*?)%s'%(n,index_list[index_list.index(n)+1]))
                    # print('章节:< %s >的， 正则表达式为: %s'%(n,res_re)) # 将列表部分元素转化成字符串，形成正则表达式
                    # print('使用下标%s'%index_len_count)
                    if list(main_dict['小说目录'][m])[index_len_count][1] not in n:
                        print('得到%s,对比 %s' % (list(main_dict['小说目录'][m])[index_len_count], n))
                    temp_dict = {
                            # '正文': self.reglux(full_text, res_re, False),
                            '卷名':m,
                            '章节名':n[len(m):],
                            '所属小说':main_dict['书名'],
                            '章节地址':list(main_dict['小说目录'][m]),
                            '更新时间':datetime.datetime.now(),
                        }
                    temp.append(temp_dict)
                    # print(temp_dict)
                    index_len_count += 1


                    # 输出成文本
                    with open('%s—%s.txt' % (m,n), 'w', encoding='utf-8') as f:
                        f.write(self.reglux(full_text, res_re, False)[0])

                    # 取出main_dict['小说目录'] : 第一卷 渴望死亡的小丑:[('2.htm', '序章 取代自我介绍的回忆—前天才美少女作家')中的元组
                    # print(main_dict['小说目录'][m])
                    # print(list(main_dict['小说目录'][m][]))

                    # if index_len_count<len(main_dict['小说目录']):
                    #     index_len_count += 1
                    # if len(test2[0])<20:
                    #     print(test2[0])
                    # else:
                    #     print(len(test2[0]))
                    # print(len(test2[0]))
                    # print(test2[0])

    def reglux(self, html_text, re_pattern, nbsp_del=True):
        '''
        正则过滤函数
        :param html_text: 字符串，网页的文本
        :param re_pattern: 字符串，正则表达式
        :param nbsp_del: 布尔值，控制是否以去除换行符的形式抓取有用信息
        :return:
        '''
        re_pattern = re_pattern.replace('~[',"\~\[").replace(']~','\]\~')
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
            recdict[ self.reglux(temp[0],self.Chapter_title,False)[0] ] = sorted(self.reglux(''.join(temp[1:]),self.Chapter_name,False))
            count += 1
        return recdict