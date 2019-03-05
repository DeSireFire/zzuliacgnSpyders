# -*- coding: utf-8 -*-
import scrapy,re,chardet,random
from Scrapy_zzuliacgn.items import nyaaItem
from Scrapy_zzuliacgn.customSettings import nyaa
class NyaaSpider(scrapy.Spider):
    name = "nyaa"
    allowed_domains = ["nyaa.si"]
    start_urls = ['http://nyaa.si']

    re_infoURL = '<ahref="/topics/view/([\s\S]*?)"target="_blank">'
    re_title = '<metaproperty="og:title"content="([\s\S]*?)::Nyaa">'
    re_info = '<div markdown-text class="panel-body" id="torrent-description">([\s\S]*?)<div class="panel panel-default">'
    re_uper = 'Uploadedby([\s\S]*?)on'
    nyaaListData = '<trclass="([\s\S]*?)"><tdstyle="padding:04px;"><ahref="/([\s\S]*?)"title="([\s\S]*?)"><imgsrc="([\s\S]*?)"alt="([\s\S]*?)"style="([\s\S]*?)"></a></td><tdcolspan="([\s\S]*?)"><ahref="([\s\S]*?)"title="([\s\S]*?)">([\s\S]*?)</a></td><tdclass="text-center"style="white-space:nowrap;"><ahref="([\s\S]*?)"><iclass="fafa-fwfa-download"></i></a><ahref="([\s\S]*?)"><iclass="fafa-fwfa-magnet"></i></a></td><tdclass="text-center">([\s\S]*?)</td><tdclass="text-center"data-timestamp="([\s\S]*?)">([\s\S]*?)</td><tdclass="text-center"style="color:green;">([\s\S]*?)</td><tdclass="text-center"style="color:red;">([\s\S]*?)</td><tdclass="text-center">([\s\S]*?)</td>'
    testlist = []
    # 该爬虫所用的数据库信息
    custom_settings = nyaa

    def parse(self, response):
        nyaaRespTe = response.text
        nyaaListDatas = self.re_Nyaa(nyaaRespTe, self.nyaaListData)
        for i in nyaaListDatas:
            Magnet = self.raplaceCharacter(i[11]).split('&tr=',1)
            rec_dict = {
                '类别': i[2],
                '标题': i[8],
                '发布时间': i[14],
                '文件大小': i[12],
                'Magnet連接': Magnet[0][20:],
                'Magnet連接typeII': Magnet[0][20:],
                '跟踪器':'&tr={}'.format(Magnet[-1]),
                '详情URL': i[7].split(r'"',1)[0],
                '资源上传数': i[15],
                '资源下载数': i[16],
                '资源完成数': i[17],
            }
            info_url = response.urljoin(i[7].split(r'"',1)[0])
            self.testlist.append(rec_dict['类别'])
            # yield scrapy.Request(url=info_url, callback=self.infoView, meta={"item": rec_dict})

        self.testlist = list(set(self.testlist))
        print(len(self.testlist))
        print(self.testlist)
        _next = response.css('body .container .center li a::attr("href")').extract()
        # 采集下一页的地址，如果最后一个元素为“#”
        if '#' not in _next[-1] :
            _next = _next[-1] # 最后一个元素必为下一页地址
            url = response.urljoin(_next)
            print(url)
            yield scrapy.Request(url=url,callback=self.parse,dont_filter=False)
        else:
            # 最后一个元素为“#”，说明爬取到底
            print('爬取结束')

    def infoView(self, response):
        rec_dict_temp = {
            '标题': self.re_Nyaa(response.text, self.re_title),
            '简介':r'<div>\r\n%s<div>\r\n</div>'%self.re_Nyaa(response.text, self.re_info,False),
            '资源发布者': self.re_Nyaa(response.text, self.re_uper),
        }
        z = {**response.meta["item"],**rec_dict_temp} # py3.5新语法，合并更新字典
        # if z['简介'] == r'<div>\r\n[]<div>\r\n</div>':
        #     print('%s 获取不到'%z['详情URL'])
        #     print(response.text)
        #     # print("".join((response.text).split()))
        # print(z['类别'])
        item = nyaaItem()
        item['rdName'] = z['标题']
        item['rdUpTime'] = z['发布时间']
        item['rdSize'] = z['文件大小']
        item['rdUpNum'] = z['资源上传数']
        item['rdDownloadNum'] = z['资源下载数']
        item['rdInfo'] = z['简介']
        item['rdOK'] = z['资源完成数']
        item['rdMagnet'] = z['Magnet連接'].split('&dn=')[0]
        item['rdMagnet2'] = z['Magnet連接typeII']
        item['rdTracker'] =z['跟踪器']
        item['rdType_id'] = z['类别']
        item['rdView'] = z['详情URL'].split('#')[0] #  'rdView': 'https://nyaa.si/view/1124001#comments '
        item['rdUper'] = z['资源发布者'][0]
        item['isdelete'] = 0
        # yield item

    def getNyaa_types(self, TypeStr):
        '''
        表Nyaa资源类别转换,初級整理
        :param typeStr: 字符串，传入类似“LiveAction-Non-English-translated”即可
        :param titleName: 字符串，传入资源的标题名
        :return: 列表
        '''
        # 小説關鍵字列表
        novelKs = ['小说','小説','novel']
        # 漫畫關鍵字列表
        comiclKs = ['漫画','漫畫','Comic','comic','コミック','週刊少年','雑誌']
        # 插畫關鍵字列表
        ImgKs = ['插畫','插画','pixiv','Pixiv','画集','畫集','P站','p站','壁纸','壁紙']
        # 照片关键字列表
        photoKs = ['照片','photo','photos','写真','寫真']

        types = {

            'LiveAction-Non-English-translated':['三次元','4'],
            'LiveAction-Idol/PromotionalVideo':['偶像/宣发','91'],
            'LiveAction-English-translated':['英翻三次元','92'],

            'Pictures-Graphics':['图像','7'],
            'Pictures-Photos':['照片','71'],

            'Audio-Lossy':['压制音乐','35'],
            'Audio-Lossless':['无损音乐','34'],

            'Literature-English-translated':['英翻漫画','24'],
            'Literature-Non-English-translated':['其他','8'], # 调用处理器细分

            'Software-Applications':['软件应用','66'],
            'Software-Games':['游戏','6'],

            'Anime-Non-English-translated': ['动漫', '1'],
            'Anime-AnimeMusicVideo':['AMV','12'],
            'Anime-English-translated':['英翻动漫','13'],

            'Anime-Raw': ['生肉', '5'],
            'Literature-Raw': ['日版漫画', '22'],
            'LiveAction-Raw': ['三次元生肉', '52'],
        }
        if TypeStr in types:
            return types[TypeStr]
        else:
            print('未识别此类别！%s'%TypeStr)
            return ['其他','8']

    def getNyaa_types_handler(self,typeStr,titleName):
        '''
        表Nyaa资源类别转换,强化整理！
        思路整理:
        首先判断是否包含汉字
        包含=>判断分类，中（港台）/日
        不包含=>判断归类，其他语言XXX

        :param typeStr: 字符串，传入类似“LiveAction-Non-English-translated”即可
        :param titleName: 字符串，传入资源的标题名
        :return: 列表
        '''
        for _char in titleName:
            if '\u4e00' <= _char <= '\u9fa5':
                print('包含汉字！')
            else:
                print('不包含汉字！')



    def re_Nyaa(self,html_text, re_pattern, nbsp_del=True):
        '''
        增则过滤函数
        :param html_text: 字符串，网页的文本
        :param re_pattern: 字符串，正则表达式
        :param nbsp_del: 布尔值，控制是否以去除换行符的形式抓取有用信息
        :return:
        '''
        pattern = re.compile(re_pattern)
        if nbsp_del:
            return pattern.findall("".join(html_text.split()))
        else:
            return pattern.findall(html_text)

    def raplaceCharacter(self,tempStr):
        '''
        替换被url编码的字符
        :param tempStr: 字符串
        :return: 转移完成的字符串
        '''
        return tempStr.replace("&amp;", "&").replace('%2F','/').replace('%3A',':')


def is_contains_chinese(strs):
    for _char in strs:
        if '\u4e00' <= _char <= '\u9fa5':
            return True
    return False

if __name__ == '__main__':
    print(is_contains_chinese('（小説）俺の家が魔力スポットだった件 ~住んでいるだけで世界最強~ 第06巻'))