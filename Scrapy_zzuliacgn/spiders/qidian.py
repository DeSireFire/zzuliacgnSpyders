# -*- coding: utf-8 -*-
import scrapy,re,os.path,json,difflib,datetime,time
# import chardet,random,datetime,

class QidianSpider(scrapy.Spider):
    name = "qidian"
    allowed_domains = ["qidian.com","560xs.com","biquge.com.cn","biqusoso.com","biquge5200.cc","xbiquge6.com","zwdu.com"]
    start_urls = ['https://book.qidian.com/info/1']

    custom_settings = {
        # 'COOKIES_ENABLED':False,
        'updateBool': False,  # 是否只爬取最新的章节,如果只爬取最新章节，未True
    }

    '''
    正则大军
    '''
    # 起点小说正则
    book_url = '<h4><a href="([\s\S]*?)" target="_blank" data-eid="([\s\S]*?)" data-bid="([\s\S]*?)">([\s\S]*?)</a></h4>\r'
    book_name_writer = '<title>《([\s\S]*?)》_([\s\S]*?)著_([\s\S]*?)_起点中文网</title>'
    book_writer_intro = '<pclass="(extend)?">([\s\S]*?)<citeclass="iconfontbluej_infoUnfold"title="展开介绍">\ue623</cite></p></div><divclass="info-wrap"data-l1="9">'
    book_writer_works = '<spanclass="book"></span><p>作品总数</p><em>([\s\S]*?)</em></li><li><spanclass="word">'
    book_writer_wordCount = '<li><spanclass="word"></span><p>累计字数</p><em>([\s\S]*?)</em></li><li><spanclass="coffee">'
    book_writer_workDays = '<p>创作天数</p><em>([\s\S]*?)</em></li></ul></div>'
    book_some = '<span class="NVxQXyDi">([\s\S]*?)</span></em><cite>'
    book_action = ' <p class="tag"><span class="blue">([\s\S]*?)</span>'
    book_intro = '<p class="intro">([\s\S]*?)</p>'
    book_introMore = '<div class="book-intro">\r                        <p>\r                            \r                                ([\s\S]*?)\r                            \r                        </p>\r                    </div>'
    book_title = r'class="iconfont">&#xe636;</b>分卷阅读</em></a>([\s\S]*?)<i>'
    book_cha = '<a class="red-btn J-getJumpUrl " href="([\s\S]*?)" id="readBtn" data-eid="qd_G03" data-bid="([\s\S]*?)" data-firstchapterjumpurl="([\s\S]*?)">'



    def start_requests(self):
        # while True:
            for page in range(1,2):
            # for page in range(1,5010):
                print("开始获取第%s页的小说"%page)
                # visited_url='https://www.qidian.com/all?&page=%s'%page
                visited_url='https://www.qidian.com/all?orderId=&style=1&pageSize=20&siteid=1&pubflag=0&hiddenField=0&page=%s'%page
                yield scrapy.Request(url=visited_url,callback=self.parse)
            # 起点全部小说也爬取完，改成只爬取最新章节
            # self.custom_settings['updateBool'] = True

    def parse(self, response):
        # print(self.reglux(response.text, self.book_url, False))
        if '暂无具体信息...' in self.reglux(response.text, self.book_url, False):
            print('爬取过快，起点小说列表获取失败！')
        for i in self.reglux(response.text, self.book_url, False):
            yield scrapy.Request(url='https://book.qidian.com/info/%s'%i[-2], callback=self.parse_novel_info,meta={'csrf':str(response.headers.getlist("Set-Cookie")[0],encoding = "utf-8").split(';')[0]})
            # time.sleep(30)


    def parse_novel_info(self, response):
        BI_resdict = {
            '书id':response.url[29:],
            '书封面':self.imgToBase64(response.url[29:]),
            '书名':self.reglux(response.text, self.book_name_writer, False)[0][0],
            '总字数':0,
            '总点击数':'',
            '阅文总点击':'',
            '会员周点击':'',
            '总推荐':'',
            '周推荐':'',
            '作者信息':{
                '作者UUID':self.time_uuid(),
                '姓名':self.reglux(response.text, self.book_name_writer, False)[0][1],
                '作者简介':self.reglux(response.text, self.book_writer_intro, True)[0][1],
                '作品总数':self.reglux(response.text, self.book_writer_works, True)[0],
                '累计字数':self.reglux(response.text, self.book_writer_wordCount, True)[0],
                '创作天数':self.reglux(response.text, self.book_writer_workDays, True)[0],
            },
            '连载状态':self.reglux(response.text, self.book_action, False)[0],
            '分类':self.reglux(response.text, self.book_name_writer, False)[0][2],
            '简介':self.reglux(response.text, self.book_intro, False)[0],
            '介绍':self.reglux(response.text, self.book_introMore, False)[0].replace('\u3000\u3000',''),
            '书源URL':response.url,
            '小说目录':{},
        }
        index_url = 'https://book.qidian.com/ajax/book/category?{csrfToken}&bookId={bookeId}'.format(csrfToken = response.meta['csrf'],bookeId = BI_resdict['书id'])
        yield scrapy.Request(url=index_url, callback=self.ajax_index, meta={"item": BI_resdict})

    def ajax_index(self,response):
        datas = json.loads(response.text)
        tempdict = response.meta['item']
        if 'data' not in datas:
            print(response.url)
            print(datas)
        indexList = []
        for i in list(datas['data']['vs']):
            for n in i['cs']:   # {'uuid': 73, 'cN': '第七十章 期待', 'uT': '2016-12-05 15:08:26', 'cnt': 2826, 'cU': '_AaqI-dPJJ4uTkiRw_sFYA2/35xIQH46UOnwrjbX3WA1AA2', 'id': 343467910, 'sS': 1}
                n['所属卷名'] = i['vN']
                tempdict['总字数'] += n['cnt'] # 字数统计
                indexList.append(self.chaster_handler(n))

        tempdict['小说目录'] = indexList

        # 起点小说的最新章节名
        tempdict['最新章节'] = tempdict['小说目录'][-1]['章节名']


        '''
        正文采集，可以根据需求进行拓展
        '''
        # 笔趣阁1
        url1 = 'https://www.biquge.com.cn/search.php?keyword=%s' % (tempdict['书名'])
        request1 = scrapy.Request(url1, callback=self.content_handler_1, meta={"item": tempdict})
        # 八一中文
        url2 = 'https://www.zwdu.com/search.php?keyword=%s' % (tempdict['书名'])
        request2 = scrapy.Request(url2, callback=self.content_handler_2, meta={"item": tempdict})
        # 560小说
        url3 = 'http://www.560xs.com/SearchBook.aspx?keyword=%s' % (tempdict['书名'])
        request3 = scrapy.Request(url3, callback=self.content_handler_3, meta={"item": tempdict})

        # # 笔趣阁2
        # url2 = 'https://www.biquge5200.cc/modules/article/search.php?searchkey=%s' % (tempdict['书名'])
        # request2 = scrapy.Request(url2, callback=self.content_handlerSecond, meta={"item": tempdict})
        # # 560小说
        # url3 = 'http://www.560xs.com/SearchBook.aspx?keyword=%s' % (tempdict['书名'])
        # request3 = scrapy.Request(url3, callback=self.content_handlerThird, meta={"item": tempdict})
        # # 笔趣阁3
        # url4 = 'https://www.xbiquge6.com/search.php?keyword=%s' % (tempdict['书名'])
        # request4 = scrapy.Request(url4, callback=self.content_handlerFourth, meta={"item": tempdict})


        # 若发现网站中不存小说或没有最新的小说章节则跳到下一个网站爬取，meta['requests']列表决定网站的顺序
        # 执行第一个request时，变量名必须一致。例如：想第一个执行request1 则 "request1.meta['requests']" 必须与 "return request1" ，“request1”其中一致。
        request1.meta['requests'] = [
            request2,
            request3,
        ]
        return request1

    def content_handler_1(self, response):
        '''
        正文通天塔第一层
        # 定位起点小说最新章节信息，例如：{'章节名': '第1399章 石罐共鸣', '更新时间': '2019-04-27 01:56:07', '字数': 3594}
        # print(response.meta['item']['小说目录'][list(response.meta['item']['小说目录'].keys())[-1]][-1]['章节名'])
        '''
        # 其他小说网站正则（用于获取小说具体地址（含所有章节表的网页地址）例如：https://www.biquge.com.cn/book/23488/）

        # 没有最新章节，去球吧
        if response.meta['item']['最新章节'] not in response.text:
            print('未查找到 %s 或未发现该书有最新章节 %s ，URL: %s 执行下一层' % (
            response.meta['item']['书名'], response.meta['item']['最新章节'], response.url))
            if response.meta['requests']:
                newRequest = response.meta['requests'].pop(0)
                newRequest.meta['requests'] = response.meta['requests']
                yield newRequest
            else:
                # 请求列表中已经无请求,pass
                pass
        else:
            names = response.xpath("/html/body/div[@class='result-list']/div[@class='result-item result-game-item']/div[@class='result-game-item-detail']/h3[@class='result-item-title result-game-item-title']/a[@class='result-game-item-title-link']/span/text()").extract()
            urls = response.xpath("/html/body/div[@class='result-list']/div[@class='result-item result-game-item']/div[@class='result-game-item-detail']/h3[@class='result-item-title result-game-item-title']/a[@class='result-game-item-title-link']/@href").extract()
            meta = {
                "item": response.meta['item'],
                'requests': response.meta['requests'],
                'xpath': [("/html/body/div[@id='wrapper']/div[@class='box_con'][2]/div[@id='list']/dl/dd/a/", 0, None,),    # 该网站的小说目录列表xpath，列表的第几个元素开始小说第一章节，列表的第几个元素最后一个章节（一般为None）
                          ("/html/body/div[@id='wrapper']/div[@class='content_read']/div[@class='box_con']/div[@id='content']", 0, None)],  # 该网站的小说正文内容列表xpath，同上（一般列表的第0个元素就是正文了，预留），同上（预留）
                'url_home': r'https://www.biquge.com.cn',   # 用于拼接小说正文的URL，某些网站用的不完整url，例如：/book/29931/15997848.html，需要拼接https://www.zwdu.com 组成：https://www.zwdu.com/book/29931/15997848.html
                'updateBool':self.custom_settings['updateBool'],# 是否只爬取最新的章节
            }
            yield scrapy.Request(url=urls[names.index(response.meta['item']['书名'])], callback=self.content_handler, meta=meta)

    def content_handler_2(self, response):
        if response.meta['item']['最新章节'] not in response.text:
            print('未查找到 %s 或未发现该书有最新章节 %s ，URL: %s 执行下一层' % (
            response.meta['item']['书名'], response.meta['item']['最新章节'], response.url))
            if response.meta['requests']:
                newRequest = response.meta['requests'].pop(0)
                newRequest.meta['requests'] = response.meta['requests']
                yield newRequest
            else:
                # 请求列表中已经无请求，pass
                pass
        else:
            names = response.xpath("/html/body/div[@class='result-list']/div[@class='result-item result-game-item']/div[@class='result-game-item-detail']/h3[@class='result-item-title result-game-item-title']/a[@class='result-game-item-title-link']/span/text()").extract()
            urls = response.xpath("/html/body/div[@class='result-list']/div[@class='result-item result-game-item']/div[@class='result-game-item-detail']/h3[@class='result-item-title result-game-item-title']/a/@href").extract()
            meta = {
                "item": response.meta['item'],
                'requests': response.meta['requests'],
                'xpath': [("/html/body/div[@id='wrapper']/div[@class='box_con'][2]/div[@id='list']/dl/dd/a/", 0, None,),
                          ("/html/body/div[@id='wrapper']/div[@class='content_read']/div[@class='box_con']/div[@id='content']", 0, None)],
                'url_home': r'https://www.zwdu.com',
                'updateBool':self.custom_settings['updateBool'],# 是否只爬取最新的章节
            }
            yield scrapy.Request(url=urls[names.index(response.meta['item']['书名'])], callback=self.content_handler ,meta=meta)

    def content_handler_3(self, response):
        if response.meta['item']['最新章节'] not in response.text:
            print('未查找到 %s 或未发现该书有最新章节 %s ，URL: %s 执行下一层' % (
            response.meta['item']['书名'], response.meta['item']['最新章节'], response.url))
            if response.meta['requests']:
                newRequest = response.meta['requests'].pop(0)
                newRequest.meta['requests'] = response.meta['requests']
                yield newRequest
            else:
                # 请求列表中已经无请求，pass
                pass
        else:
            names = response.xpath("/html/body/div[@id='wrapper']/div[@id='main']/div[@class='novelslist2']/ul/li[2]/span[@class='s2']/a/text()").extract()
            urls = response.xpath("/html/body/div[@id='wrapper']/div[@id='main']/div[@class='novelslist2']/ul/li[2]/span[@class='s2']/a/@href").extract()
            meta = {
                "item": response.meta['item'],
                'requests': response.meta['requests'],
                'xpath': [
                    ("/html/body/div[@id='wrapper']/div[@class='box_con'][2]/div[@id='list']/dl/dd/a/", 12, None,),# 章节
                    ("/html/body/div[@class='content_read']/div[@class='box_con']/div[@id='content']", 0, None),# 正文
                ],
                'url_home': r'http://www.560xs.com',
                'updateBool':self.custom_settings['updateBool'],# 是否只爬取最新的章节
            }
            yield scrapy.Request(url='http://www.560xs.com%s' % urls[names.index(response.meta['item']['书名'])], callback=self.content_handler, meta=meta)

    def content_handler(self,response):
        '''
        正文采集函数
        :param [i['章节名'] for i in response.meta['item']['小说目录']]:起点目录列表
        :param list(set(nameList).difference(set(tempList))):在笔趣阁目录，但不在起点目录的集合
        :param list(set([i['章节名'] for i in response.meta['item']['小说目录']]).difference(set(tempList))):在起点目录，但不在笔趣阁目录的集合
        :return:
        '''
        # 第三方小说站的小说目录里的URL列表和章节的名字列表
        urlList = response.xpath(response.meta['xpath'][0][0]+'@href').extract()[response.meta['xpath'][0][1]:response.meta['xpath'][0][2]]
        nameList = response.xpath(response.meta['xpath'][0][0]+'text()').extract()[response.meta['xpath'][0][1]:response.meta['xpath'][0][2]]

        # 小说基础信息表管道
        self.qItem(response.meta['item'])

        # 作者信息表管道
        self.qWriterItem(response.meta['item']['作者信息'])

        if len(nameList) != len(response.meta['item']['小说目录']):
                if response.meta['updateBool']:# 是否只爬取最新的章节
                    info = {
                        '文章顺序': len(nameList),
                        '所属小说名': response.meta['item']['书名'],
                        '所属卷名': '正文卷',
                        '章节名': nameList[-1],
                        '更新时间': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        '字数': 0,
                    }
                    yield scrapy.Request(url=response.meta['url_home'] + urlList[-1], callback=self.content_downLoader,meta={"item": info, 'xpath': response.meta['xpath'][1]})
                else:
                    for name, url in zip(nameList, urlList):
                        info = {
                            '文章顺序': nameList.index(name) + 1,
                            '所属小说名': response.meta['item']['书名'],
                            '所属卷名': '正文卷',
                            '章节名': name,
                            '更新时间': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            '字数': 0,
                            '正文':'',
                        }
                        yield scrapy.Request(url=response.meta['url_home'] + url, callback=self.content_downLoader,meta={"item": info, 'xpath': response.meta['xpath'][1]})
        else:
            for url, info in zip(urlList, response.meta['item']['小说目录']):
                yield scrapy.Request(url=response.meta['url_home'] + url, callback=self.content_downLoader,meta={"item": info, 'xpath': response.meta['xpath'][1]})




    def content_downLoader(self,response):

        response.meta['item']['正文'] = self.clearHtml(response.xpath(response.meta['xpath'][0]).extract()[0])
        # response.meta['item']['正文'] = self.clearHtml(response.xpath(response.meta['xpath'][0]).extract()[response.meta['xpath'][1]:response.meta['xpath'][2]])
        response.meta['item']['字数'] = len(self.clearHtml(response.xpath(response.meta['xpath'][0]).extract()[0]))

        # 小说正文内容管道
        self.qChapterItem(response.meta['item'])

        # # print(len(response.xpath(response.meta['xpath'][0]).extract()))
        # with open(os.path.join(os.getcwd(),'log','qidian','%s.txt'%response.meta['item']['章节名']), 'w', encoding='utf-8') as f:
        #     # f.write(response.xpath(response.meta['xpath'][0]).extract()[response.meta['xpath'][1]:response.meta['xpath'][2]])
        #     f.write(self.clearHtml(response.xpath(response.meta['xpath'][0]).extract()[0]))


    def qItem(self,tempDict):
        '''
        小说基础信息
        :param tempDict:你懂的
        :return:
        '''
        from qdScrapySpyder.items import QidianItem
        item = QidianItem()
        item['bImgBase64'] = tempDict['书封面']  # 封面
        item['bName'] = tempDict['书名']  # 书名
        item['bKeys'] = tempDict['总字数']  # 总字数
        item['bResClick'] = tempDict['总点击数']  # 总点击数
        item['bClick'] = tempDict['阅文总点击']  # 阅文总点击
        item['bVIPClick'] = tempDict['会员周点击']  # 会员周点击
        item['bResRecommend'] = tempDict['总推荐']  # 总推荐
        item['bWeekRecommend'] = tempDict['周推荐']  # 周推荐
        item['bWriterName'] = tempDict['作者信息']['作者UUID']  # 作者UUID
        item['bAction'] = tempDict['连载状态']  # 连载状态
        item['bType'] = tempDict['分类']  # 分类
        item['bIntro'] = tempDict['简介']  # 简介
        item['bMoreIntro'] = tempDict['介绍']  # 介绍
        item['bURL'] = tempDict['书源URL']  # 书源URL
        # item['bIndex'] = tempDict['小说目录']  # 小说目录
        item['isD'] = 0  # 是否属于删除状态
        yield item

    def qChapterItem(self, tempDict):
        '''
        小说正文
        :param tempDict:你懂的
        :return:
        '''
        from qdScrapySpyder.items import QidianChapterItem
        item = QidianChapterItem()
        item['cOrder'] = tempDict['文章顺序']  # '文章顺序'
        item['cBook'] = tempDict['所属小说名']  # '所属卷名'
        item['cTitle'] = tempDict['所属卷名']  # '所属卷名'
        item['cName'] = tempDict['章节名']  # '章节名'
        item['cUT'] = tempDict['更新时间']  # '更新时间'
        item['cKeys'] = tempDict['字数']  # '字数'
        item['cContent'] = tempDict['正文']  # '字数'
        item['isD'] = 0  # 是否属于删除状态
        yield item

    def qWriterItem(self, tempDict):
        '''
        小说作者信息
        :param tempDict:你懂的
        :return:
        '''
        from qdScrapySpyder.items import QidianWriterItem
        item = QidianWriterItem()
        item['wUUID'] = tempDict['作者UUID']  # 作者UUID
        item['wName'] = tempDict['姓名']  # 姓名
        item['wItro'] = tempDict['作者简介']  # 作者简介
        item['wWorks'] = tempDict['作品总数']  # 作品总数
        item['wWorkKeys'] = tempDict['累计字数']  # 累计字数
        item['wWorkDays'] = tempDict['创作天数']  # 创作天数
        item['isD'] = 0  # 是否属于删除状态
        yield item


    # 工具函数
    def fontAnti(self,):
        '''
        todo 字体反爬
        :return:
        '''
        # from fontTools.ttLib import TTFont
        # 没戏没戏
        pass

    def imgToBase64(self,imgId):
        '''
        小说封面图获取并转base64
        :param imgId: 字符串，小说在起点的id编号
        :return: base64码
        '''
        import requests, base64
        myheader = {
            'Host': 'bookcover.yuewen.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36',
        }
        # print("封面地址：https://bookcover.yuewen.com/qdbimg/349573/%s/180"%imgId)
        req = requests.get(url="https://bookcover.yuewen.com/qdbimg/349573/%s/180"%imgId, headers=myheader)
        base64_data = base64.b64encode(req.content)
        return 'data:image/jpg;base64,' + bytes.decode(base64_data)

    def time_uuid(self):
        '''
        生成uuid1
        :return: 基于MAC地址、当前时间戳、随机数生成。
        '''
        import uuid
        return uuid.uuid1()

    def CtoE(self,tempStr):
        '''
        中文符号转英文符号
        :param tempStr: 字符串
        :return:
        '''
        table = {ord(f): ord(t) for f, t in zip(
            u'，。！？【】（）％＃＠＆１２３４５６７８９０',
            u',.!?[]()%#@&1234567890')}
        return tempStr.translate(table)

    def string_similar(self,s1, s2):
        '''
        字符串相似度
        :param s1:字符串,用于比较的字符串
        :param s2:字符串,被比较的字符串
        :return:
        '''
        return difflib.SequenceMatcher(None, s1, s2).quick_ratio()

    def clearHtml(self,tempStr):
        '''
        清除html标签,
        :param tempStr: 字符串,需要清洗html的字符串
        :return:
        '''
        # todo ㈧㈠Δ』中文网Ｗｗ％Ｗ．ん８⒈Ｚｗ．ＣＯＭ沙雕字符清洗
        return re.sub(r'</?\w+[^>]*>', '', tempStr)

    def chaster_handler(self,temp):
        '''
        章节信息整理
        :param temp:字典，整理例如：{'uuid': 4, 'cN': '第一章 他叫白小纯', 'uT': '2016-04-28 11:32:50', 'cnt': 3059, 'cU': 'rJgN8tJ_cVdRGoWu-UQg7Q2/6jr-buLIUJSaGfXRMrUjdw2', 'id': 306873415, 'sS': 1}的信息
        :return:
        '''
        return {
            '所属卷名':temp['所属卷名'],
            '章节名':temp['cN'],
            '更新时间':temp['uT'],
            '字数':temp['cnt'],
        }

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