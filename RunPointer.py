from scrapy import cmdline
#Scrapy默认是不能在IDE中调试的，需要以下操作
cmdline.execute(['scrapy','crawl','dmhy'])
cmdline.execute(['scrapy','crawl','dmhyUpdate'])
# cmdline.execute(['scrapy','crawl','nyaa'])
cmdline.execute(['scrapy','crawl','wenku8'])
#前两个参数是不变的，第三个参数请使用自己的spider的名字


