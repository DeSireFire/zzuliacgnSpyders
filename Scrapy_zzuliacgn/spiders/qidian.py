# -*- coding: utf-8 -*-
import scrapy,re,chardet,random,datetime,os.path,json


class QidianSpider(scrapy.Spider):
    name = "qidian"
    allowed_domains = ["qidian.com"]
    start_urls = ['https://book.qidian.com/info/1']

    # custom_settings = {}

    book_url = '<h4><a href="([\s\S]*?)" target="_blank" data-eid="qd_B58" data-bid="([\s\S]*?)">([\s\S]*?)</a></h4>\r'
    book_name_writer = '<title>《([\s\S]*?)》_([\s\S]*?)著_([\s\S]*?)_起点中文网</title>'
    book_action = ' <p class="tag"><span class="blue">([\s\S]*?)</span>'
    book_intro = '<p class="intro">([\s\S]*?)</p>'
    book_introMore = '<div class="book-intro">\r                        <p>\r                            \r                                ([\s\S]*?)\r                            \r                        </p>\r                    </div>'
    # book_introMore = '<div class="book-intro">\r                        <p>\r                            \r                                \u3000\u3000在破败中崛起，在寂灭中复苏。<br>\u3000\u3000沧海成尘，雷电枯竭，那一缕幽雾又一次临近大地，世间的枷锁被打开了，一个全新的世界就此揭开神秘的一角……\r                            \r                        </p>\r                    </div>'
    book_title = r'class="iconfont">&#xe636;</b>分卷阅读</em></a>([\s\S]*?)<i>'
    book_cha = '<a class="red-btn J-getJumpUrl " href="([\s\S]*?)" id="readBtn" data-eid="qd_G03" data-bid="([\s\S]*?)" data-firstchapterjumpurl="([\s\S]*?)">'

    def start_requests(self):

        for page in range(1,2):
            print("开始获取第%s页的小说"%page)
            visited_url='https://www.qidian.com/all?&page=%s'%page
            yield scrapy.Request(url=visited_url,callback=self.parse)

    def parse(self, response):
        for i in self.reglux(response.text, self.book_url, False):
            yield scrapy.Request(url='https://book.qidian.com/info/%s'%i[1], callback=self.parse_novel_info,meta={'csrf':str(response.headers.getlist("Set-Cookie")[0],encoding = "utf-8").split(';')[0]})


    def parse_novel_info(self, response):

        BI_resdict = {
            '书id':response.url[29:],
            '书名':self.reglux(response.text, self.book_name_writer, False)[0][0],
            '作者':self.reglux(response.text, self.book_name_writer, False)[0][1],
            '连载状态':self.reglux(response.text, self.book_action, False)[0],
            '分类':self.reglux(response.text, self.book_name_writer, False)[0][2],
            '简介':self.reglux(response.text, self.book_intro, False)[0],
            '介绍':self.reglux(response.text, self.book_introMore, False)[0].replace('\u3000\u3000',''),
            '书源URL':response.url,
            '小说目录':{},
        }
        print(BI_resdict)
        # with open('%s.txt'%BI_resdict['书名'], 'w', encoding='utf-8') as f:
        #     f.write(str([response.text]))
        index_url = 'https://book.qidian.com/ajax/book/category?{csrfToken}&bookId={bookeId}'.format(csrfToken = response.meta['csrf'],bookeId = BI_resdict['书id'])
        yield scrapy.Request(url=index_url, callback=self.ajax_index, meta={"item": BI_resdict})

    def ajax_index(self,response):
        datas = json.loads(response.text)
        tempdict = response.meta['item']
        if 'data' not in datas:
            print(response.url)
            print(datas)
        # for i in list(datas['data']['vs']):
        #     tempdict['小说目录']['%s[%s]'%(i['vN'],list(datas['data']['vs']).index(i))] = i['cs']
        # print(tempdict)
        # # # 输出成文本
        # with open('%s.txt'%response.meta['item']['书名'], 'w', encoding='utf-8') as f:
        #     f.write(str(tempdict))


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