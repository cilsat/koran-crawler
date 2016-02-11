import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings
from multiprocessing import Process

def korancrawler(spider, year, cp):
    cp.crawl(spider, str(year))
    cp.start()

c = CrawlerProcess(get_project_settings())
configure_logging({'LOG_FILE': '/home/cilsat/dev/koran-crawler/output/crawl.log'})

years = [2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016]
spiders = ['republika', 'tempo', 'kompas', 'metro']

processes = []
for spider in spiders:
    for year in years:
        p = Process(target=korancrawler, args=(spider, year, c))
        p.start()
        processes.append(p)

for p in processes:
    p.join()

