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
    novelName = scrapy.Field() # 小说名
    writer = scrapy.Field() # 作者名
    illustrator = scrapy.Field() # 插画师名
    fromPress = scrapy.Field()  # 文库名
    intro = scrapy.Field() # 小说简介
    headerImage = scrapy.Field() # 小说封面
    resWorksNum = scrapy.Field() # 小说字数
    types = scrapy.Field() #小说所属类型


    action = scrapy.Field() # 连载状态

    # saveTime = scrapy.Field() # 小说收录时间,最旧的章节时间为收录时间

class wenku8ChapterItem:
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
    novel_title = scrapy.Field() # 小说册名
    chapter = scrapy.Field() # 章节名
    worksNum = scrapy.Field() # 章节名
    container = scrapy.Field() # 正文
    updateTime = scrapy.Field()  # 小说更新时间，最新的章节时间为更新时间
    chapterImgurls = scrapy.Field() # 该章节的插画