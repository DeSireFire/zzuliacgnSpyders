# -*- coding: utf-8 -*-
from Scrapy_zzuliacgn.tools import config
import random
# Scrapy settings for Scrapy_zzuliacgn project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#     http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#     http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'Scrapy_zzuliacgn'

SPIDER_MODULES = ['Scrapy_zzuliacgn.spiders']
NEWSPIDER_MODULE = 'Scrapy_zzuliacgn.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
# USER_AGENT = 'Scrapy_zzuliacgn (+http://www.yourdomain.com)'
# USER_AGENT = random.choice(config.USER_AGENTS)

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 16

# Configure a delay for requests for the same website (default: 0)
# See http://scrapy.readthedocs.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
# DEFAULT_REQUEST_HEADERS = config.get_header()

# Enable or disable spider middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html
SPIDER_MIDDLEWARES = {
    'scrapy.spidermiddlewares.httperror.HttpErrorMiddleware': 50,
    'scrapy.spidermiddlewares.offsite.OffsiteMiddleware': 500,
    'scrapy.spidermiddlewares.referer.RefererMiddleware': 700,
    'scrapy.spidermiddlewares.urllength.UrlLengthMiddleware': 800,
    'scrapy.spidermiddlewares.depth.DepthMiddleware': 900,
}
# Enable or disable downloader middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    # 'scrapy.downloadermiddlewares.robotstxt.RobotsTxtMiddleware': 100,
    # 'scrapy.downloadermiddlewares.httpauth.HttpAuthMiddleware': 300,
    # 'scrapy.downloadermiddlewares.downloadtimeout.DownloadTimeoutMiddleware': 350,
    # 'scrapy.downloadermiddlewares.defaultheaders.DefaultHeadersMiddleware': 400,
    # 'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': 500,
    # 'scrapy.downloadermiddlewares.retry.RetryMiddleware': 550,
    # 'scrapy.downloadermiddlewares.ajaxcrawl.AjaxCrawlMiddleware': 560,
    # 'scrapy.downloadermiddlewares.redirect.MetaRefreshMiddleware': 580,
    # 'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 590,
    # 'scrapy.downloadermiddlewares.redirect.RedirectMiddleware': 600,
    # 'scrapy.downloadermiddlewares.cookies.CookiesMiddleware': 700,
    # 'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 750,
    # 'scrapy.downloadermiddlewares.stats.DownloaderStats': 850,
    # 'scrapy.downloadermiddlewares.httpcache.HttpCacheMiddleware': 900,
    'Scrapy_zzuliacgn.middlewares.RandomUserAgentMiddleware': 554,
    'Scrapy_zzuliacgn.middlewares.ProxyMiddleware': 555,
}

# Enable or disable extensions
# See http://scrapy.readthedocs.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See http://scrapy.readthedocs.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
   'Scrapy_zzuliacgn.pipelines.mysqlPipeline': 300,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See http://doc.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
# 初始下载延迟
# AUTOTHROTTLE_START_DELAY = 60
# The maximum download delay to be set in case of high latencies
# 在高延迟的情况下设置的最大下载延迟
# AUTOTHROTTLE_MAX_DELAY = 240
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 0
HTTPCACHE_DIR = 'httpcache'
HTTPCACHE_IGNORE_HTTP_CODES = []
HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

# 修改编码为utf-8
# FEED_EXPORT_ENCODING = 'utf-8'
# FEED_EXPORT_ENCODING = 'GB2312'

# 数据库信息
# MYSQL配置
# 默认
MYSQL_HOST = '192.168.37.128' # 数据库地址
MYSQL_DATABASE = 'zzuli_ACGN' # 数据库名
MYSQL_USER = 'zzuliACGN'
MYSQL_PASSWORD = 'DeSireFire233notRoot'
MYSQL_PORT = 3306


# 代理设置
PROXY_URL = 'http://192.168.37.128:5010/get/'


RETRY_TIMES = 10