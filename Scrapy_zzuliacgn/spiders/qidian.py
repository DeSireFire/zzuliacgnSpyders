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
    book_url = '<h4><a href="([\s\S]*?)" target="_blank" data-eid="qd_B58" data-bid="([\s\S]*?)">([\s\S]*?)</a></h4>\r'
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
            visited_url='https://www.qidian.com/all?&page=%s'%page
            yield scrapy.Request(url=visited_url,callback=self.parse)

    def parse(self, response):
        # print(self.reglux(response.text, self.book_url, False))
        for i in self.reglux(response.text, self.book_url, False)[:1]:
            yield scrapy.Request(url='https://book.qidian.com/info/%s'%i[1], callback=self.parse_novel_info,meta={'csrf':str(response.headers.getlist("Set-Cookie")[0],encoding = "utf-8").split(';')[0]})


    def parse_novel_info(self, response):
        BI_resdict = {
            '书id':response.url[29:],
            '书名':self.reglux(response.text, self.book_name_writer, False)[0][0],
            '总字数':'',
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
        # print(BI_resdict['作者信息'])
        # print(BI_resdict['书名'])

        index_url = 'https://book.qidian.com/ajax/book/category?{csrfToken}&bookId={bookeId}'.format(csrfToken = response.meta['csrf'],bookeId = BI_resdict['书id'])
        yield scrapy.Request(url=index_url, callback=self.ajax_index, meta={"item": BI_resdict})

    def ajax_index(self,response):
        datas = json.loads(response.text)
        tempdict = response.meta['item']
        if 'data' not in datas:
            print(response.url)
            print(datas)
        for i in list(datas['data']['vs']):
            tempdict['小说目录']['%s[%s]'%(i['vN'],list(datas['data']['vs']).index(i))] = []
            for n in i['cs']:
                tempdict['小说目录']['%s[%s]' % (i['vN'], list(datas['data']['vs']).index(i))].append(self.chaster_handler(n))

        # todo 此处可把小说基础信息item通过tempdict入库
        # print(tempdict)

        # todo 正文内容的开始
        url1 = 'https://www.biquge.com.cn/search.php?keyword=%s'%(tempdict['书名'])
        request1 = scrapy.Request(url1, callback=self.content_handlerFirst, meta={"item": tempdict})

        url2 = 'https://www.biquge5200.cc/modules/article/search.php?searchkey=%s'%(tempdict['书名'])
        request2 = scrapy.Request(url2, callback=self.content_handlerSecond, meta={"item": tempdict})

        url3 = 'http://www.560xs.com/SearchBook.aspx?keyword=%s'%(tempdict['书名'])
        request3 = scrapy.Request(url3, callback=self.content_handlerThird, meta={"item": tempdict})

        url4 = 'https://wap.xbiquge6.com/search.php?keyword=%s'%(tempdict['书名'])
        request4 = scrapy.Request(url4, callback=self.content_handlerFourth, meta={"item": tempdict})

        url5 = 'https://m.zwdu.com/search.php?keyword=%s'%(tempdict['书名'])
        request5 = scrapy.Request(url5, callback=self.content_handlerFourth, meta={"item": tempdict})


        request1.meta['requests'] = [
            request2,
            request3,
            request4,
            request5,
        ]
        return request1



    def content_handlerFirst(self,response):
        '''
        正文通天塔第一层

        # 定位起点小说最新章节信息，例如：{'章节名': '第1399章 石罐共鸣', '更新时间': '2019-04-27 01:56:07', '字数': 3594}
        # print(response.meta['item']['小说目录'][list(response.meta['item']['小说目录'].keys())[-1]][-1]['章节名'])
        '''
        # 其他小说网站正则（用于获取小说具体地址（含所有章节表的网页地址）例如：https://www.biquge.com.cn/book/23488/）
        bookURL = '<a cpos="title" href="([\s\S]*?)" title="%s" class="result-game-item-title-link" target="_blank">'%response.meta['item']['书名']
        print(self.reglux(response.text, bookURL, False))

        # 判断可能存在系列续集小说名字不对应的情况，例如：“斗罗大陆III龙王传说”变成“龙王传说”才能检索到
        if '暂无' in self.reglux(response.text, bookURL, False)[0] or response.meta['item']['小说目录'][list(response.meta['item']['小说目录'].keys())[-1]][-1]['章节名'] not in response.text:
            print('未查找到该书或未发现该书有最新章节，执行 planB')
            print(response.url)
            print(response.meta['item']['书名'])
            return response.meta['requests'].pop(0)
        else:
            # [('https://www.biquge.com.cn/book/23488/', '圣墟')]
            yield scrapy.Request(url=self.reglux(response.text, bookURL, False)[0], callback=self.content_handler, meta={"item": response.meta['item']})

    def content_handlerSecond(self,response):
        bookURL = '<td class="odd"><a href="([\s\S]*?)">%s</a></td>'%response.meta['item']['书名']
        print(self.reglux(response.text, bookURL, False))
        if '暂无' in self.reglux(response.text, bookURL, False)[0] or response.meta['item']['小说目录'][list(response.meta['item']['小说目录'].keys())[-1]][-1]['章节名'] not in response.text:
            print('未查找到该书或未发现该书有最新章节，执行 planC')
            print(response.url)
            print(response.meta['item']['书名'])
            return response.meta['requests'].pop(0)
        else:
            yield scrapy.Request(url=self.reglux(response.text, bookURL, False)[0], callback=self.content_handler, meta={"item": response.meta['item']})

    def content_handlerThird(self,response):
        bookURL = '</span><spanclass="s2"><ahref="([\s\S]*?)"target="_blank">%s</a></span><spanclass="s3"><ahref="'%response.meta['item']['书名']
        if '暂无' in self.reglux(response.text, bookURL, True)[0] or response.meta['item']['小说目录'][list(response.meta['item']['小说目录'].keys())[-1]][-1]['章节名'] not in response.text:
            print('未查找到该书或未发现该书有最新章节，执行 planD')
            print(response.url)
            print(response.meta['item']['书名'])
            return response.meta['requests'].pop(0)
        else:
            yield scrapy.Request(url='http://www.560xs.com%s'%self.reglux(response.text, bookURL, True)[0], callback=self.content_handler, meta={"item": response.meta['item']})

    def content_handlerFourth(self, response):
        bookURL = '<a cpos="title" href="([\s\S]*?)" title="%s" class="result-game-item-title-link" target="_blank">'%response.meta['item']['书名']
        print(self.reglux(response.text, bookURL, False))
        if '暂无' in self.reglux(response.text, bookURL, False)[0] or response.meta['item']['小说目录'][list(response.meta['item']['小说目录'].keys())[-1]][-1]['章节名'] not in response.text:
            print('未查找到该书或未发现该书有最新章节，执行 planF')
            print(response.url)
            print(response.meta['item']['书名'])
            return response.meta['requests'].pop(0)
        else:
            yield scrapy.Request(url=self.reglux(response.text, bookURL, False)[0],callback=self.content_handler, meta={"item": response.meta['item']})

    def content_handlerFifth(self, response):
        bookURL = '<a cpos="title" href="([\s\S]*?)" title="%s" class="result-game-item-title-link" target="_blank">'%response.meta['item']['书名']
        print(response.text)
        print(self.reglux(response.text, bookURL, False))
        if '暂无' in self.reglux(response.text, bookURL, False)[0] or response.meta['item']['小说目录'][list(response.meta['item']['小说目录'].keys())[-1]][-1]['章节名'] not in response.text:
            print('未查找到该书或未发现该书有最新章节，执行 planF')
            print(response.url)
            print(response.meta['item']['书名'])
            # return response.meta['requests'].pop(0)
        else:
            yield scrapy.Request(url=self.reglux(response.text, bookURL, False)[0],callback=self.content_handler, meta={"item": response.meta['item']})

    def content_handler(self,response):
        '''
        正文采集函数
        :param response:
        :return:
        '''
        print(response.text)
        # print(response.meta['item']['小说目录'])
        for m in response.meta['item']['小说目录']:
            for n in response.meta['item']['小说目录'][m]:
                print(self.reglux(response.text, '<dd><a href="([\s\S]*?)">%s</a></dd>'%n['章节名'], False))
        # print(str("".join(response.text.split())))
        # if '站内搜索' in response.text:
        #     print(response.text)
        # with open(os.path.join(os.getcwd(),'log','qidian','%s.txt'%response['item']['书名']), 'w', encoding='utf-8') as f:
        #     f.write(str("".join(response.text.split())))

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

    def chaster_handler(self,temp):
        '''
        {'uuid': 4, 'cN': '第一章 他叫白小纯', 'uT': '2016-04-28 11:32:50', 'cnt': 3059, 'cU': 'rJgN8tJ_cVdRGoWu-UQg7Q2/6jr-buLIUJSaGfXRMrUjdw2', 'id': 306873415, 'sS': 1}
        :param temp:
        :return:
        '''
        return {
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