# Scrapy settings for dirbot project

SPIDER_MODULES = ['dirbot.spiders']
NEWSPIDER_MODULE = 'dirbot.spiders'
DEFAULT_ITEM_CLASS = 'dirbot.items.Art'

LOG_ENABLED = True
CONCURRENT_REQUESTS = 100
CONCURRENT_REQUESTS_PER_IP = 8

ITEM_PIPELINES = {'dirbot.pipelines.FilterWordsPipeline': 1}
