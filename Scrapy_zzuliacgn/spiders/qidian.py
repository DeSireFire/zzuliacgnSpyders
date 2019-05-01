# -*- coding: utf-8 -*-
import scrapy,re,chardet,random,datetime,os.path,json


class QidianSpider(scrapy.Spider):
    name = "qidian"
    allowed_domains = ["qidian.com","560xs.com","biquge.com.cn","biqusoso.com","biquge5200.cc","xbiquge6.com","zwdu.com"]
    start_urls = ['https://book.qidian.com/info/1']

    # custom_settings = {
    #     # 'COOKIES_ENABLED':False,
    # }

    '''
    增则大军
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
        for page in range(1,2):
            print("开始获取第%s页的小说"%page)
            # visited_url='https://www.qidian.com/all?&page=%s'%page
            visited_url='https://www.qidian.com/all?orderId=&style=1&pageSize=20&siteid=1&pubflag=0&hiddenField=0&page=%s'%page
            yield scrapy.Request(url=visited_url,callback=self.parse)

    def parse(self, response):
        print(self.reglux(response.text, self.book_url, False))
        if '暂无具体信息...' in self.reglux(response.text, self.book_url, False):
            print(response.text)
        for i in self.reglux(response.text, self.book_url, False)[6:8]:
            print(i)
            yield scrapy.Request(url='https://book.qidian.com/info/%s'%i[-2], callback=self.parse_novel_info,meta={'csrf':str(response.headers.getlist("Set-Cookie")[0],encoding = "utf-8").split(';')[0]})


    def parse_novel_info(self, response):
        BI_resdict = {
            '书id':response.url[29:],
            '书名':self.reglux(response.text, self.book_name_writer, False)[0][0],
            '总字数':0,
            '总点击数':'',
            '阅文总点击':'',
            '会员周点击':'',
            '总推荐':'',
            '周推荐':'',
            '作者信息':{
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

        # 最新章节名
        tempdict['最新章节'] = tempdict['小说目录'][-1]['章节名']

        # todo 此处可把小说基础信息item通过tempdict入库
        # print(tempdict) item{......}

        # todo 正文内容的开始
        url1 = 'https://www.biquge.com.cn/search.php?keyword=%s'%(tempdict['书名'])
        request1 = scrapy.Request(url1, callback=self.content_handlerFirst, meta={"item": tempdict})

        url2 = 'https://www.biquge5200.cc/modules/article/search.php?searchkey=%s'%(tempdict['书名'])
        request2 = scrapy.Request(url2, callback=self.content_handlerSecond, meta={"item": tempdict})

        url3 = 'http://www.560xs.com/SearchBook.aspx?keyword=%s'%(tempdict['书名'])
        request3 = scrapy.Request(url3, callback=self.content_handlerThird, meta={"item": tempdict})

        url4 = 'https://www.xbiquge6.com/search.php?keyword=%s'%(tempdict['书名'])
        request4 = scrapy.Request(url4, callback=self.content_handlerFourth, meta={"item": tempdict})

        url5 = 'https://m.zwdu.com/search.php?keyword=%s'%(tempdict['书名'])
        request5 = scrapy.Request(url5, callback=self.content_handlerFourth, meta={"item": tempdict})


        request4.meta['requests'] = [
            request2,
            request3,
            request4,
            request5,
        ]

        return request4



    def content_handlerFirst(self,response):
        '''
        正文通天塔第一层

        # 定位起点小说最新章节信息，例如：{'章节名': '第1399章 石罐共鸣', '更新时间': '2019-04-27 01:56:07', '字数': 3594}
        # print(response.meta['item']['小说目录'][list(response.meta['item']['小说目录'].keys())[-1]][-1]['章节名'])
        '''
        # 其他小说网站正则（用于获取小说具体地址（含所有章节表的网页地址）例如：https://www.biquge.com.cn/book/23488/）
        bookURL = '<a cpos="title" href="([\s\S]*?)" title="%s" class="result-game-item-title-link" target="_blank">'%response.meta['item']['书名']
        # 判断可能存在系列续集小说名字不对应的情况，例如：“斗罗大陆III龙王传说”变成“龙王传说”才能检索到
        if '暂无' in self.reglux(response.text, bookURL, False)[0] or response.meta['item']['最新章节'] not in response.text:
            print('未查找到该书或未发现该书有最新章节，执行 planB')
            newRequest = response.meta['requests'].pop(0)
            newRequest.meta['requests'] = response.meta['requests']
            yield newRequest
        else:
            # self.reglux(response.text, bookURL, False) = [('https://www.biquge.com.cn/book/23488/', '圣墟')]
            meta = {
                "item": response.meta['item'],
                'requests': response.meta['requests'],
                'xpath':[("/html/body/div[@id='wrapper']/div[@class='box_con'][2]/div[@id='list']/dl/dd/a/",0,None,),
                         # ("/html/body/div[@id='wrapper']/div[@class='content_read']/div[@class='box_con']/div[@id='content']/text()",0,None)],
                         ("/html/body/div[@id='wrapper']/div[@class='content_read']/div[@class='box_con']/div[@id='content']",0,None)],
                'url_home':r'https://www.biquge.com.cn',
            }
            yield scrapy.Request(url=self.reglux(response.text, bookURL, False)[0], callback=self.content_handler, meta=meta)

    def content_handlerSecond(self,response):
        '''
        这个网站，速度不够快啊，可能需要代理了
        '''
        bookURL = '<td class="odd"><a href="([\s\S]*?)">%s</a></td>'%response.meta['item']['书名']
        print(self.reglux(response.text, bookURL, False))
        if '暂无' in self.reglux(response.text, bookURL, False)[0] or response.meta['item']['最新章节'] not in response.text:
            print('未查找到 %s 或未发现该书有最新章节，执行 planC' % response.meta['item']['书名'])
            newRequest = response.meta['requests'].pop(0)
            newRequest.meta['requests'] = response.meta['requests']
            yield newRequest
        else:
            meta = {
                "item": response.meta['item'],
                'requests': response.meta['requests'],
                'xpath':[("/html/body/div[@id='wrapper']/div[@class='box_con'][2]/div[@id='list']/dl/dd/a/",9,None,),
                         ("/html/body/div[@id='wrapper']/div[@class='content_read']/div[@class='box_con']/div[@id='content']",0,None)],
                'url_home':r'',
            }
            yield scrapy.Request(url=self.reglux(response.text, bookURL, False)[0], callback=self.content_handler, meta=meta)

    def content_handlerThird(self,response):
        bookURL = '</span><spanclass="s2"><ahref="([\s\S]*?)"target="_blank">%s</a></span><spanclass="s3"><ahref="'%response.meta['item']['书名']
        print(self.reglux(response.text, bookURL, True))
        if '暂无' in self.reglux(response.text, bookURL, True)[0] or response.meta['item']['最新章节'] not in response.text:
            print('未查找到 %s 或未发现该书有最新章节，执行 planD'%response.meta['item']['书名'])
            newRequest = response.meta['requests'].pop(0)
            newRequest.meta['requests'] = response.meta['requests']
            # yield newRequest
        else:
            meta = {
                "item": response.meta['item'],
                'requests': response.meta['requests'],
                'xpath':[("/html/body/div[@id='wrapper']/div[@class='box_con'][2]/div[@id='list']/dl/dd/a/",12,None,),
                         ("/html/body/div[@class='content_read']/div[@class='box_con']/div[@id='content']",0,None)],
                'url_home':r'http://www.560xs.com',
            }
            yield scrapy.Request(url='http://www.560xs.com%s'%self.reglux(response.text, bookURL, True)[0], callback=self.content_handler, meta=meta)

    def content_handlerFourth(self, response):
        bookURL = '<a cpos="title" href="([\s\S]*?)" title="%s" class="result-game-item-title-link" target="_blank">'%response.meta['item']['书名']
        print(self.reglux(response.text, bookURL, False))
        # if '暂无' in self.reglux(response.text, bookURL, False)[0]:
        if '暂无' in self.reglux(response.text, bookURL, False)[0] or response.meta['item']['最新章节'] not in response.text:
            print('未查找到 %s 或未发现该书有最新章节，执行 planF' % response.meta['item']['书名'])
            newRequest = response.meta['requests'].pop(0)
            newRequest.meta['requests'] = response.meta['requests']
            # yield newRequest
        else:
            meta = {
                "item": response.meta['item'],
                'requests': response.meta['requests'],
                'xpath':[("/html/body/div[@id='wrapper']/div[@class='box_con'][2]/div[@id='list']/dl/dd/a/",0,None,),
                         ("/html/body/div[@id='wrapper']/div[@class='content_read']/div[@class='box_con']/div[@id='content']",0,None)],
                'url_home':r'https://www.xbiquge6.com',
            }
            yield scrapy.Request(url=self.reglux(response.text, bookURL, False)[0],callback=self.content_handler, meta=meta)

    def content_handlerFifth(self, response):
        bookURL = '<a cpos="title" href="([\s\S]*?)" title="%s" class="result-game-item-title-link" target="_blank">'%response.meta['item']['书名']
        print(response.text)
        print(self.reglux(response.text, bookURL, False))
        if '暂无' in self.reglux(response.text, bookURL, False)[0] or response.meta['item']['最新章节'] not in response.text:
            print('未查找到该书或未发现该书有最新章节，执行 planF')
            print(response.url)
            print(response.meta['item']['书名'])
        else:
            yield scrapy.Request(url=self.reglux(response.text, bookURL, False)[0],callback=self.content_handler, meta={"item": response.meta['item'],'requests':response.meta['requests']})

    def content_handler(self,response):
        '''
        正文采集函数
        :param response:
        :return:
        '''
        urlList = response.xpath(response.meta['xpath'][0][0]+'@href').extract()[response.meta['xpath'][0][1]:response.meta['xpath'][0][2]]
        # # 章节对齐
        if len(urlList) != len(response.meta['item']['小说目录']):
            nameList = response.xpath(response.meta['xpath'][0][0]+'text()').extract()[response.meta['xpath'][0][1]:response.meta['xpath'][0][2]]
            for i in response.meta['item']['小说目录']:
                if i['章节名'] not in nameList and '第' not in i['章节名']:    # 坑哭了['第三百四十五章 太有灵性了', '第四百四十六章 抓神兽幼崽', '第三百四十七章 神秘幼崽',] 垃圾网站章节标错
                    print('%s 章节内容未在该网找到。'%i)
                    response.meta['item']['小说目录'].remove(i)
        for url,info in zip(urlList,response.meta['item']['小说目录']):
            yield scrapy.Request(url=response.meta['url_home']+url,callback=self.content_downLoader, meta={"item": info,'xpath':response.meta['xpath'][1]})

    def content_downLoader(self,response):
        # print(len(response.xpath(response.meta['xpath'][0]).extract()))
        with open(os.path.join(os.getcwd(),'log','qidian','%s.txt'%response.meta['item']['章节名']), 'w', encoding='utf-8') as f:
            # f.write(response.xpath(response.meta['xpath'][0]).extract()[response.meta['xpath'][1]:response.meta['xpath'][2]])
            f.write(self.clearHtml(response.xpath(response.meta['xpath'][0]).extract()[0]))

    # def number_handler(self,numberStr):
    #     '''
    #     例如：https://book.qidian.com/info/1004608738中，针对字数等信息采用字体反爬的对策方案
    #     :param numberStr:字符串，例如：“&#100525;&#100528;&#100521;&#100526;&#100527;&#100530;”
    #     :return: 字符串
    #     '''
    #     number_dict = {
    #         "&#100526;":'.',
    #         "&#100527;":'0',
    #         "&#100529;":'1',
    #         "&#100521;":'2',
    #         "&#100531;":'3',
    #         "&#100525;":'4',
    #         "&#100532;":'4',
    #         "&#100523;":'6',
    #         "&#100524;":'7',
    #         "&#100530;":'8',
    #         "&#100528;":'9',
    #     }
    #     for i in number_dict:
    #         numberStr = numberStr.replace(i,number_dict[i])
    #     return numberStr
    def clearHtml(self,tempStr):
        '''
        清除html标签,

        :param tempStr: 字符串
        :return:
        '''
        # todo ㈧㈠Δ』中文网Ｗｗ％Ｗ．ん８⒈Ｚｗ．ＣＯＭ沙雕字符清洗
        return re.sub(r'</?\w+[^>]*>', '', tempStr)

    def chaster_handler(self,temp):
        '''
        {'uuid': 4, 'cN': '第一章 他叫白小纯', 'uT': '2016-04-28 11:32:50', 'cnt': 3059, 'cU': 'rJgN8tJ_cVdRGoWu-UQg7Q2/6jr-buLIUJSaGfXRMrUjdw2', 'id': 306873415, 'sS': 1}
        :param temp:
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