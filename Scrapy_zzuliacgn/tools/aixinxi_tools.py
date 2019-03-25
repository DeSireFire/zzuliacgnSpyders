import requests,re,json,hashlib
# from Spyder.aixinxi.aixinxi_config import *
# from aixinxi.aixinxi_config import *
from Scrapy_zzuliacgn.tools.aixinxi_config import *

# 登陆aixinxi
def login():
    """

    :return:登陆成功后返回cookie
    """
    header = get_header()
    req1 = requests.post(url=login_url, headers=header, data=login_dirt)
    # req1 = requests.post(url=login_url, headers=header, data=login_dirt, proxies=proxy_list())
    if req1.status_code == 200:
        header.update({'cookie':req1.headers['Set-Cookie'][:36],'referer':'https://tu.aixinxi.net/views/pages.php?id=explore','upgrade-insecure-requests':'1',})
        if logining(header):
            print('登陆成功！')
            return header
        else:
            print('登陆失败！')
            return False
    else:
        return False

# 检测当前cooke的登陆状态
def logining(header):
    """

    :param header: 字典，请求头
    :return: 布尔值
    """
    req = requests.post(url=index_url, headers=header)
    # req = requests.post(url=index_url, headers=header, proxies=proxy_list())
    if '<a href="https://tu.aixinxi.net/views/login.php"><i class="fa fa-user" aria-hidden="true"></i> 登录/注册</a>' not in req.text:

        return True
    else:
        return False

# 读取文件列表
def userFiles(header):
    """

    :param header: 字典，请求头
    :return: 列表，所有图片文件名和key,例如：[('6472a56c546d31de83a1xxxxxxxx', 'o_1cq3oq991g0q1lt3121t04boka.jpg'),]
    """
    header['referer'] = 'https://tu.aixinxi.net/views/userFiles.php'
    page = 1
    imgdata = []
    while page != 0:
        url = 'https://tu.aixinxi.net/views/userFiles.php?page=%s' % (page)
        req = requests.post(url=url, headers=header)
        pattern = re.compile(r'<td><a style="color:#000" target="_blank" href="https://tu.aixinxi.net/views/fileJump.php\?key=(.*?)&ming=(.*?)">管理</a>', re.S)
        tempfilesList = re.findall(pattern, req.text)
        if tempfilesList:
            imgdata += tempfilesList
            page += 1
        else:
            page = 0
    return imgdata

# 上传并保存文件
def updata(header,fileName,filesRead):
    """

    :param header: 请求头部
    :param filesRead: 已经读取过的文件数据，例如：filesRead = {'file': open('1.jpg', 'rb')}
    :param filesRead: 字符串，带后缀的文件名，例如：xxx.png
    :return: 布尔值
    """
    if 'referer' in header:
        del header['referer']
        header.update(update_header)
    else:
        header.update(update_header)

    # 获取上传的地址
    req_ossurl = requests.post(url=index_url, headers=header)
    new_update_url = re.findall('upserver ="(.*?)";var', req_ossurl.text)[0]
    print('获取上传地址:%s'%new_update_url)
    if new_update_url:
        update_url = new_update_url

    temp_data = token_get(header)
    if temp_data:
        print(temp_data)
        update_data.update(temp_data)
        # update_data['policy'] = temp_data['policy']
        # update_data['signature'] = temp_data['signature']
        # update_data['OSSAccessKeyId'] = temp_data['AccessKeyId']
        update_data['name'] = fileName
        update_data['key'] = fileName
    else:
        print("token获取失败")
        return False
    req = requests.post(url=update_url, headers=header, data=update_data, files=filesRead)
    print(req)
    if req.status_code == 200:
        print('上传成功！')
        info = save(header,fileName)
        if info:
            print('保存成功！')
            print(info)
            return info
        else:
            print('保存失败！')
            return False
    else:
        print("上传失败！")
        print(req.text)
        print(req.headers)
        return False

# 保存文件
def save(header,fileName):
    """
    da2293e8d43a8decf0136c6ee44c0f20,jpg,
    {'Server': 'Tengine', 'Date': 'Mon, 12 Nov 2018 12:18:32 GMT', 'Content-Type': 'text/html; charset=UTF-8', 'Transfer-Encoding': 'chunked', 'Connection': 'keep-alive', 'Vary': 'Accept-Encoding', 'X-Powered-By': 'PHP/5.6.30', 'Expires': 'Thu, 19 Nov 1981 08:52:00 GMT', 'Cache-Control': 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0', 'Pragma': 'no-cache', 'Content-Encoding': 'gzip'}
    ['04d1cff3e980155df7538088166d0446,png,']
    {'Server': 'Tengine', 'Date': 'Mon, 12 Nov 2018 12:24:09 GMT', 'Content-Type': 'text/html; charset=UTF-8', 'Transfer-Encoding': 'chunked', 'Connection': 'keep-alive', 'Vary': 'Accept-Encoding', 'X-Powered-By': 'PHP/5.6.30', 'Expires': 'Thu, 19 Nov 1981 08:52:00 GMT', 'Cache-Control': 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0', 'Pragma': 'no-cache', 'Content-Encoding': 'gzip'}

    :param header: 请求头
    :param fileName: 文件名
    :return:列表，例如：[da2293e8d43a8decf0136c6ee44c0f20,jpg,]
    """
    header.update(save_header)
    data_save['ming'] = fileName
    req = requests.post(url=save_url, headers=header, data=data_save)
    return req.text.split(',')[:2]

# 删除图片
def delete(header,key):
    """
    {'User-Agent': 'Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)', 'cookie': 'PHPSESSID=gb9b12bgkn4a8gv1mf2ur50ud3', 'referer': 'https://tu.aixinxi.net/views/pic.php?key=da2293e8d43a8decf0136c6ee44c0f20', 'upgrade-insecure-requests': '1', 'origin': 'https://tu.aixinxi.net'}
    ok.删除成功
    {'Server': 'Tengine', 'Date': 'Mon, 12 Nov 2018 12:38:01 GMT', 'Content-Type': 'text/html; charset=UTF-8', 'Transfer-Encoding': 'chunked', 'Connection': 'keep-alive', 'Vary': 'Accept-Encoding', 'X-Powered-By': 'PHP/5.6.30', 'Content-Encoding': 'gzip'}
    :param header: 请求头部
    :param key: 图片的key
    :return:布尔值
    """
    header.update(delete_header)
    header['referer'] += key
    data_delete['key'] = key
    req = requests.post(url=delete_url, headers=header, data=data_delete)
    # req = requests.post(url=delete_url, headers=header, data=data_delete, proxies=proxy_list())
    if 'ok' in req.text:
        print('OK')
        print(req.status_code)
        print(req.text)
        print(req.headers)
        return True
    else:
        print(req.status_code)
        print(req.text)
        print(req.headers)
        return False

# 查找图片信息
def filesFind(header,fileName):
    """

    :param header: 请求头
    :param fileName: 需要查询的文件名
    :return: 列表，[key,fileName] 例如：['1b655e2a822747c3c78af0859ca1b63c', 'o_1cq3gdm9jqcm11g87jv1ghiqaea.jpg']
    """
    fileslist = userFiles(header)
    for t in fileslist:
        if fileName in t:
            fileslist = list(t)
            print(fileslist)
            return fileslist

# token密钥获取
def token_get(header):
    """
    {'policy': 'xx', 'signature': 'xx', 'AccessKeyId': 'xx'}/False
    :param header: 请求头部
    :return: 成功，传回字典；失败传回False
    """
    header.update(token_header)
    del header['upgrade-insecure-requests']
    req = requests.get(url=token_url, headers=header)
    if req.status_code == 200:
        return json.loads(req.text)
    else:
        print('token请求失败！')
        return False

# 文件名生成器
def fileNameIter():
    hash_md5 = hashlib.md5(fileName_data)
    return hash_md5.hexdigest()

# 退出aixinxi
def loginOutloginOut(outcookie):
    """

    :param outcookie: 传入已经登陆了的cookie值
    :return:
    """
    loginOut_Header['cookie'] = outcookie
    req = requests.post(url=loginOut_url, headers=loginOut_Header, data=loginOut_dirt, verify=False)
    if req.status_code == 200:
        print('退出成功！')
        return True
    else:
        return False
    # print(req.status_code)
    # print(req.text)
    # print(req.encoding)
    # print(req.reason)
    # print(req.headers)

# def proxy_list(url = PROXYURL,testURL = testURL):
#     """
#     获取并检测代理池返回的IP
#     :param url: 获取IP的代理池地址
#     :param testURL: 检测网址
#     :return: 一个能用的ip组成的proxies字典
#     """
#     count = 0 # 获取的IP数
#     try:
#         r = requests.get(url)
#         count = len(json.loads(r.text))
#         while count != 0:
#             r = requests.get(url)
#             ip_ports = json.loads(r.text)
#             count = len(ip_ports)
#             for i in range(0,4):
#                 ip = ip_ports[i][0]
#                 port = ip_ports[i][1]
#                 proxies = {
#                     'http': 'http://%s:%s' % (ip, port),
#                     'https': 'https://%s:%s' % (ip, port)
#                 }
#                 r = requests.get(testURL, proxies=proxies,timeout=TIMEOUT)
#                 if (not r.ok) or len(r.content) < 500:
#                     r = requests.get(delproxyIP%(ip,port))
#                 else:
#                     return proxies
#
#     except Exception as e:
#         # print(e)
#         return None

def main():

    # 登陆爱信息图床并返回有关头部信息
    # ok = login()
    # if ok:
    #     print(ok)
    # else:
    #     print('No')

    # 使用头部信息访问首页，判断是否登陆成功
    # a = logining(header=ok)
    # print(a)

    # 查询操作
    # 查询该登录账号在爱信息图床所有的图片名
    # fl = userFiles(ok)
    # print(fl)

    # 删除操作
    # 按照爱信息图床返回的图片key,来删除图片
    # delete(ok,'44764c752081126b509b12091356f56c')

    # 添加操作（上传文件）+保存
    # 以二进制方式读取本地文件到内存
    # f = open('1.txt', 'r',encoding='UTF-8')
    # # f = open('yiyayiyayo.jpg', 'rb')
    # files = {'file':f}
    # 上传函数包括以下步骤：
    # 1.传入登陆的头信息、打算保存在图床的文件名、文件二进制码
    # 2.先调整上传的头部信息
    # 3.向目标首页发送请求，获取具体上传的OSS服务器地址
    # 4.向目标网站发送请求，获取对应的osskey信息，并加入到待发送的data中
    # 5.对oss存储服务器地址，发送带key的data,以及上传文件，获取返回值信息
    # 6.将返回信息保存到自己对应的图床账号，以便管理
    # 注意，updata方法，内置了token_get、save两个方法。使用updata方法以后不需要单独调用save、token_get方法。除非需要单独测试
    # updata(ok,'o_233qwe6667788.txt',files)
    # 关闭文件读取，释放内存
    # f.close()

    # 其他操作
    # 将图片信息保存到自己图床账号，方便管理，不建议单独使用
    # save(header_test,'o_1chq3v5e43um1bocaru1iqn7b8c.gif')

    # 获取osskey信息
    # print(token_get(ok))

    # 账号退出，短时间登陆过多次账户而不退出，会出现提示禁止登陆
    # 传入已登陆的cookie值
    # loginOutloginOut(ok['cookie'])
    loginOutloginOut('PHPSESSID=s535jgjvaqotsnbn1j7u9b3h32')

    # 文件名随机生成
    # print(fileNameIter())

if __name__ == '__main__':
    main()