import config
import spyder.HtmlHandler
from spyder.HtmlDownloader import Html_Downloader

def wenku8(parser):
    # print(parser["urls"][0])
    c = spyder.HtmlDownloader
    req = c.Html_Downloader.download(config.parserList[0]["urls"][0])
    if req:
        if spyder.HtmlHandler.endDetection(req):
            info = spyder.HtmlHandler.reglux_list(config.parserList[0]["pattern"]["novel_info"],req)
            print(info)
            if spyder.HtmlHandler.responseAgain(info):
                # 需要二次请求
                req = c.Html_Downloader.download(info["responseAgain"][0])
                # print(req)
                if req:
                    # print(config.parserList[0]["pattern"]["Chapter"])
                    # Chapter = spyder.HtmlHandler.reglux_list(config.parserList[0]["pattern"]["Chapter"],req)
                    Chapter = spyder.HtmlHandler.reglux_list({'tbody':'<tr>([\s\S]*?)</tr>',},req)
                    spyder.HtmlHandler.titleCheck(Chapter["tbody"],config.parserList[0]["pattern"]["Chapter"])

            else:
                # 不需要二次请求，于当前页完成内容爬取
                print("不需要二次请求，于当前页完成内容爬取")

        else:
            print("到达尽头！")
    else:
        print(req)
        print("请求失败，建议continue")

def titleCheck(tlist):
    tids = []   # 筛选出“原矿”列表中，所有册名的下标
    for i in tlist:
        if 'class="vcss"' in i:
            tids.append(tlist.index(i))
    count = 0
    recdict = {}
    while count+1 < len(tids):# 使用卷名下标来对列表中属于章节的部分切片出来
        temp = tlist[tids[count]:tids[count + 1]]
        if count+1 == len(tids)-1:
            temp=tlist[tids[count + 1]:]
        recdict[temp[0]] = ''.join(temp[1:])
        count +=1
    for m,n in recdict.items():
        print('%s:%s'%(m,n))


if __name__ == '__main__':
    wenku8(config.parserList[0])