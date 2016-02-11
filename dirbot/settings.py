# Scrapy settings for dirbot project

SPIDER_MODULES = ['dirbot.spiders']
NEWSPIDER_MODULE = 'dirbot.spiders'
DEFAULT_ITEM_CLASS = 'dirbot.items.Art'

LOG_ENABLED = True
CONCURRENT_REQUESTS = 200
CONCURRENT_REQUESTS_PER_IP = 20

ITEM_PIPELINES = {'dirbot.pipelines.FilterWordsPipeline': 1}
DOWNLOADER_MIDDLEWARES= {'scrapy.downloadermiddlewares.cookies.CookiesMiddleware': 543}

FEED_FORMAT = 'xml'
FEED_URI = '/home/cilsat/dev/koran-crawler/output/output.xml'
