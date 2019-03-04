# -*- coding: utf-8 -*-
import scrapy,re,chardet,random
from Scrapy_zzuliacgn.items import nyaaItem
class NyaaSpider(scrapy.Spider):
    name = "nyaa"
    allowed_domains = ["nyaa.si"]
    start_urls = ['http://nyaa.si/']

    re_infoURL = '<ahref="/topics/view/([\s\S]*?)"target="_blank">'
    # re_time = '<li>發佈時間:<span>([\s\S]*?)</span></li>'
    # re_type = '<tdstyle="padding:04px;"><ahref="([\s\S]*?)_([\s\S]*?)"title="([\s\S]*?)">'
    # re_title = '<divclass="topic-titleboxui-corner-all"><h3>([\s\S]*?)</h3>'
    # re_size = '<li>文件大小:<span>([\s\S]*?)</span></li>'
    re_info = '<div markdown-text="" class="panel-body" id="torrent-description">([\s\S]*?)<div>\r\n</div>'
    # re_magnet1 = '<aclass="magnet"id="a_magnet"href="([\s\S]*?)">([\s\S]*?)</a>'
    # re_magnet2 = '<aid="magnet2"href="([\s\S]*?)">([\s\S]*?)</a>'
    re_uper = 'data-toggle="tooltip"title="User">([\s\S]*?)</a>'
    # re_UDO_DATA = '<tdnowrap="nowrap"align="center"><spanclass="btl_1">([\s\S]*?)</span></td><tdnowrap="nowrap"align="center"><spanclass="bts_1">([\s\S]*?)</span></td><tdnowrap="nowrap"align="center">([\s\S]*?)</td><tdalign="center"><ahref="([\s\S]*?)">([\s\S]*?)</a></td>'
    nyaaListData = '<trclass="([\s\S]*?)"><tdstyle="padding:04px;"><ahref="/([\s\S]*?)"title="([\s\S]*?)"><imgsrc="([\s\S]*?)"alt="([\s\S]*?)"style="([\s\S]*?)"></a></td><tdcolspan="([\s\S]*?)"><ahref="([\s\S]*?)"title="([\s\S]*?)">([\s\S]*?)</a></td><tdclass="text-center"style="white-space:nowrap;"><ahref="([\s\S]*?)"><iclass="fafa-fwfa-download"></i></a><ahref="([\s\S]*?)"><iclass="fafa-fwfa-magnet"></i></a></td><tdclass="text-center">([\s\S]*?)</td><tdclass="text-center"data-timestamp="([\s\S]*?)">([\s\S]*?)</td><tdclass="text-center"style="color:green;">([\s\S]*?)</td><tdclass="text-center"style="color:red;">([\s\S]*?)</td><tdclass="text-center">([\s\S]*?)</td>'
    # 该爬虫所用的数据库信息
    # custom_settings = dmhy

    def parse(self, response):
        nyaaRespTe = response.text
        # print("".join(nyaaRespTe.split()))
        nyaaListDatas = self.re_Nyaa(nyaaRespTe, self.nyaaListData)
        print(len(nyaaListDatas))
        print(nyaaListDatas[1])
        # test = self.re_Nyaa(response.text, self.re_info,False)
        # test = self.re_Nyaa(response.text, self.re_uper,False)
        # print(test)
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
                '详情URL': 'https://nyaa.si%s'%i[7].split(r'"',1)[0],
                '资源上传数': i[15],
                '资源下载数': i[16],
                '资源完成数': i[17],
            }
            yield scrapy.Request(url=rec_dict["详情URL"], callback=self.infoView, meta={"item": rec_dict})
            print(rec_dict)


    def infoView(self, response):
        rec_dict_temp = {
            '简介':r'<div>\r\n%s<div>\r\n</div>'%self.re_Nyaa(response.text, self.re_info,False),
            '资源发布者': self.re_Nyaa(response.text, self.re_uper)[0],
        }
        z = {**response.meta["item"],**rec_dict_temp} # py3.5新语法，合并更新字典
        item = nyaaItem()
        item['rdName'] = z['标题']
        item['rdUpTime'] = z['发布时间']
        item['rdSize'] = z['文件大小']
        item['rdUpNum'] = z['资源上传数']
        item['rdDownloadNum'] = z['资源下载数']
        item['rdInfo'] = z['简介']
        item['rdOK'] = z['资源完成数']
        item['rdMagnet'] = z['Magnet連接']
        item['rdMagnet2'] = z['Magnet連接typeII']
        item['rdTracker'] =z['跟踪器']
        item['rdType_id'] = z['类别']
        item['rdView'] = z['详情URL'] #  'rdView': 'https://share.dmhy.org/topics/view/511931_AngelEcho_70.html'}
        item['rdUper'] = z['资源发布者']
        item['isdelete'] = 0
        print(item)
        # yield item

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
        # return tempStr.replace("&amp;", "&").replace('%2F','/').replace('%3A',':').replace('%7d','}').replace('%7b','{')