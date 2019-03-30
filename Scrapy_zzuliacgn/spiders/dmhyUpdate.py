# -*- coding: utf-8 -*-
import scrapy,re,chardet,random
from Scrapy_zzuliacgn.items import dmhyItem
from Scrapy_zzuliacgn.customSettings import dmhy

class DmhySpider(scrapy.Spider):
    '''
    流程： 首先向start_urls地址发送请求，得到的response都会返回到函数parse,通过选择器抓取响应的内容，然后再获取下一页的地址，发送请求。
    '''
    name = "dmhyUpdate"
    allowed_domains = ["share.dmhy.org"]
    start_urls = ['https://share.dmhy.org']

    re_infoURL = '<ahref="/topics/view/([\s\S]*?)"target="_blank">'
    re_time = '<li>發佈時間:<span>([\s\S]*?)</span></li>'
    re_type = '<tdwidth="6%"align="center"><aclass="([\s\S]*?)"href="'
    re_title = '<divclass="topic-titleboxui-corner-all"><h3>([\s\S]*?)</h3>'
    re_size = '<li>文件大小:<span>([\s\S]*?)</span></li>'
    re_info = '<strong>簡介:&nbsp;</strong>([\s\S]*?)<a name="description-end"></a>'
    re_magnet1 = '<aclass="magnet"id="a_magnet"href="([\s\S]*?)">([\s\S]*?)</a>'
    re_magnet2 = '<aid="magnet2"href="([\s\S]*?)">([\s\S]*?)</a>'
    re_FileList = '<div class="file_list">([\s\S]*?)</div>'
    re_UDO_DATA = '<tdnowrap="nowrap"align="center"><spanclass="btl_1">([\s\S]*?)</span></td><tdnowrap="nowrap"align="center"><spanclass="bts_1">([\s\S]*?)</span></td><tdnowrap="nowrap"align="center">([\s\S]*?)</td><tdalign="center"><ahref="([\s\S]*?)">([\s\S]*?)</a></td>'
    # 该爬虫所用的数据库信息
    custom_settings = dmhy

    def parse(self, response):
        a_i_u_e_o = response.text
        ha_hi_fu_he_ho = list(map(lambda x: self.getDMHY_types('viewInfoURL') + x, self.re_DMHY(a_i_u_e_o, self.re_infoURL)))
        sa_shi_su_se_so = self.re_DMHY(a_i_u_e_o, self.re_type)
        UDOs = self.re_DMHY(a_i_u_e_o, self.re_UDO_DATA)
        for ma_mi_mu_me_mo, na_ni_nu_ne_no, re_UDO in zip(ha_hi_fu_he_ho, sa_shi_su_se_so,UDOs):
            rec_dict = {
                '类别': self.getDMHY_types(na_ni_nu_ne_no),
                '标题': '',
                '发布时间': '',
                '文件大小': '',
                'Magnet連接': '',
                'Magnet連接typeII': '',
                '简介': r'<div>\r\n' + '',
                '详情URL': ma_mi_mu_me_mo,
                '资源发布者': re_UDO[4],
                '资源上传数': re_UDO[0],
                '资源下载数': re_UDO[1],
                '资源完成数': re_UDO[2],
            }
            yield scrapy.Request(url=rec_dict["详情URL"], callback=self.infoView, meta={"item": rec_dict})
        _next = response.css('.nav_title .fl a::attr("href")').extract()
        # 采集下一页的地址，如果有两个元素说明为存在上下页地址
        if '/topics/list/page/11' not in _next :
            _next = _next[-1] # 第二个元素必为下一页地址
            url = response.urljoin(_next)
            print(url)
            yield scrapy.Request(url=url,callback=self.parse,dont_filter=False)
        else:
            _next = 'https://www.dmhy.org'
            yield scrapy.Request(url=_next, callback=self.parse, dont_filter=False)


    def infoView(self, response):
        rec_dict_temp = {
            '标题':self.urlDecode(self.re_DMHY(response.text, self.re_title)[0]),
            '发布时间':self.timeMaker(self.re_DMHY(response.text, self.re_time)[0]),
            '文件大小':self.re_DMHY(response.text, self.re_size)[0],
            'Magnet連接':list(self.re_DMHY(response.text, self.re_magnet1)[0]),
            'Magnet連接typeII':list(self.re_DMHY(response.text, self.re_magnet2)[0]),
            '简介':self.re_DMHY(response.text, self.re_info,False)[0][:-7].replace('\t','').replace('\n',''),
            '文件列表':re.sub(' src="/images/icon/(.*?).gif"','',self.re_DMHY(response.text, self.re_FileList,False)[0].replace('\t','').replace('\n','').replace('><img align="middle" ',' '),)
        }
        z = {**response.meta["item"],**rec_dict_temp} # py3.5新语法，合并更新字典
        item = dmhyItem()
        item['rdName'] = z['标题']
        item['rdUpTime'] = z['发布时间']
        item['rdSize'] = z['文件大小']
        item['rdUpNum'] = z['资源上传数']
        item['rdDownloadNum'] = z['资源下载数']
        item['rdInfo'] = z['简介']
        item['rdOK'] = z['资源完成数']
        item['rdMagnet'] = z['Magnet連接'][1][20:]
        item['rdMagnet2'] = z['Magnet連接typeII'][0][20:]
        item['rdTracker'] =z['Magnet連接'][0][len(z['Magnet連接'][1]):][4:]
        item['rdFileList'] =z['文件列表']
        item['rdType_id'] = z['类别'][1]
        item['rdView'] = z['详情URL'].split('_',1)[1] #  'rdView': 'https://share.dmhy.org/topics/view/511931_AngelEcho_70.html'}
        item['rdUper'] = z['资源发布者']
        item['isdelete'] = 0
        yield item

    def getDMHY_types(self, TypeStr):
        '''
        动漫花园资源类别转换
        :param _str: 字符串，传入类似“sort-2”即可
        :return: 字符串
        '''
        types = {
            'sort-2': ['动画','1'],
            'sort-31': ['季度全集', '11'],
            'sort-3': ['漫画', '2'],
            'sort-41': ['港台漫画', '21'],
            'sort-42': ['日版漫画', '22'],
            'sort-4': ['音乐', '3'],
            'sort-43': ['动漫音乐', '31'],
            'sort-44': ['同人音乐', '32'],
            'sort-15': ['流行音乐', '33'],
            'sort-6': ['日剧', '41'],
            'sort-12': ['特摄', '42'],
            'sort-7': ['RAW', '5'],
            'sort-9': ['游戏', '6'],
            'sort-17': ['电脑游戏', '61'],
            'sort-18': ['电视游戏', '62'],
            'sort-19': ['掌机游戏', '63'],
            'sort-20': ['网络游戏', '64'],
            'sort-21': ['游戏周边', '65'],
            'sort-1': ['其他', '9'],
            'viewInfoURL': 'https://share.dmhy.org/topics/view/',
        }
        if TypeStr in types:
            return types[TypeStr]
        else:
            print('未识别此类别！%s'%TypeStr)
            return ['其他','8']

    def re_DMHY(self,html_text, re_pattern, nbsp_del=True):
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

    def timeMaker(self0,time_str):
        '''
        由于动漫花园的资源发布时间没有秒，该函数用来添加秒数，并整理时间格式
        :param time_str: 传入例如：2019/02/1222:09等14或15位长度的时间字符串
        :return:整理好的时间字符串
        '''
        return "{} {}:{}{}.{}".format('-'.join(time_str[:10].split('/')), time_str[10:],random.randint(0,5),random.randint(0,9),''.join(str(random.choice(range(10))) for i in range(6)))

    def urlDecode(self,tempStr):
        '''
        用于转换url编码的特殊符号，例如&amp;转&
        :param tempStr: 需要替换的字符串
        :return: 字符串类型，tempStr
        '''
        # url编码的字符串
        urlencode = ['&amp;']
        # url解码的字符串
        urldecode = ['&']
        for n,m in zip(urlencode,urldecode):
            tempStr = tempStr.replace(n,m)
        return tempStr