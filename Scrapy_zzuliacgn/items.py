# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ScrapyBtItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class QuoteItem(scrapy.Item):
    text = scrapy.Field()
    author = scrapy.Field()
    tags = scrapy.Field()

class dmhyItem(scrapy.Item):
    rdName = scrapy.Field()#资源名称
    rdUpTime = scrapy.Field()#资源发布时间
    rdSize = scrapy.Field()#资源大小
    rdUpNum = scrapy.Field()#资源上传数
    rdDownloadNum = scrapy.Field()#资源下载数
    rdInfo = scrapy.Field()#资源介绍
    rdOK = scrapy.Field()#资源完成数
    rdMagnet = scrapy.Field()#资源下载链接
    rdMagnet2 = scrapy.Field()#资源下载链接
    rdTracker = scrapy.Field()#资源下tracker服务器
    rdFileList = scrapy.Field()#资源文件列表
    rdType_id =scrapy.Field()#资源种类
    rdView = scrapy.Field()#资源详细页地址
    rdUper = scrapy.Field()#资源发布者
    isdelete = scrapy.Field()#资源详细页地址

class nyaaItem(scrapy.Item):
    rdName = scrapy.Field()#资源名称
    rdUpTime = scrapy.Field()#资源发布时间
    rdSize = scrapy.Field()#资源大小
    rdUpNum = scrapy.Field()#资源上传数
    rdDownloadNum = scrapy.Field()#资源下载数
    rdInfo = scrapy.Field()#资源介绍
    rdOK = scrapy.Field()#资源完成数
    rdMagnet = scrapy.Field()#资源下载链接
    rdMagnet2 = scrapy.Field()#资源下载链接
    rdTracker = scrapy.Field()#资源下tracker服务器
    rdType_id =scrapy.Field()#资源种类
    rdView = scrapy.Field()#资源详细页地址
    rdUper = scrapy.Field()#资源发布者
    isdelete = scrapy.Field()#资源详细页地址

class wenku8Item(scrapy.Item):
    novelName = scrapy.Field()  # 小说名
    writer = scrapy.Field()  # 作者名
    illustrator = scrapy.Field()    # 插画师名
    fromPress = scrapy.Field()  # 文库名
    intro = scrapy.Field()  # 小说简介
    headerImage = scrapy.Field()    # 小说封面
    resWorksNum = scrapy.Field()    # 小说字数
    types_id = scrapy.Field()   #小说所属类型
    action = scrapy.Field()    # 连载状态
    isdelete = scrapy.Field()  # 资源详细页地址
    contents = scrapy.Field()    # 小说字数
    # saveTime = scrapy.Field() # 小说收录时间,最旧的章节时间为收录时间

class wenku8ChapterItem(scrapy.Item):
    '''
    思路记录：
    由于小说主体内容过大，所以不适合保存在后端服务器；
    采取存储在第三方的方式，并保存相应的保存地址，通过后台发送请求获取文章正文；
    novel_container 预计存储格式如下：
    [[小说章节名1,保存地址1],[小说章节名2,保存地址2],[小说章节名3,保存地址3]..]
    小说章节数，则以该列表的下标+1的方式记录。

    狗屁，真难，存是能存了，增量更新如何解决？？
    '''
    name = scrapy.Field() # 所属书名
    title = scrapy.Field() # 小说册名
    chapter = scrapy.Field() # 章节名
    fullName = scrapy.Field() # 章节全称（用于防止重复，唯一约束）
    worksNum = scrapy.Field() # 章节字数
    updateTime = scrapy.Field()  # 小说更新时间，最新的章节时间为更新时间
    chapterImgurls = scrapy.Field() # 该章节的插画
    container = scrapy.Field() # 正文
    isdelete = scrapy.Field()  # 资源详细页地址

'''
字段名与类中的变量名相同即可
其中，QidianItem中的bWriterName对应的是QidianWriterItem的wUUID
'''
class QidianItem(scrapy.Item):
    '''
    表名：QidianItem
    变量名对应数据库字段名
    '''
    bName = scrapy.Field()    # 书名
    bKeys = scrapy.Field()    # 总字数
    bResClick = scrapy.Field()    # 总点击数（预留）
    bClick = scrapy.Field()    # 阅文总点击（预留）
    bVIPClick = scrapy.Field()    # 会员周点击（预留）
    bResRecommend = scrapy.Field()    # 总推荐（预留）
    bWeekRecommend = scrapy.Field()    # 周推荐（预留）
    bWriterName = scrapy.Field()    # 作者UUID
    bAction = scrapy.Field()    # 连载状态
    bType = scrapy.Field()    # 分类
    bIntro = scrapy.Field()    # 简介
    bMoreIntro = scrapy.Field()    # 介绍
    bURL = scrapy.Field()    # 书源URL
    # bIndex = scrapy.Field()    # 小说目录（没必要）
    bImgBase64 = scrapy.Field()    # 封面
    isD = scrapy.Field()    # 是否属于删除状态

class QidianChapterItem(scrapy.Item):
    '''
    表名：QidianChapterItem
    变量名对应数据库字段名
    '''
    cOrder = scrapy.Field()  # '所属小说顺序'
    cBook = scrapy.Field()  # '所属小说名'
    cTitle = scrapy.Field()  # '所属卷名'
    cName = scrapy.Field()  # '章节名'
    cUT = scrapy.Field()  # '更新时间'
    cKeys = scrapy.Field()  # '字数'
    cContent = scrapy.Field()  # '字数'
    isD = scrapy.Field()    # 是否属于删除状态

class QidianWriterItem(scrapy.Item):
    '''
    表名：QidianWriterItem
    变量名对应数据库字段名
    '''
    wUUID = scrapy.Field()  # 作者UUID
    wName = scrapy.Field()  # 姓名
    wItro = scrapy.Field()  # 作者简介
    wWorks = scrapy.Field() # 作品总数
    wWorkKeys = scrapy.Field()  # 累计字数
    wWorkDays = scrapy.Field()  # 创作天数
    isD = scrapy.Field()    # 是否属于删除状态