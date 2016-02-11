#!/usr/bin/python

import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings

from multiprocessing import Process
import argparse

def korancrawler(cp, spider, year=None):
    if year:
        cp.crawl(spider, str(year))
    else:
        cp.crawl(spider)
    cp.start()

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Crawl Indonesian newspaper sites.')
    parser.add_argument('-s', '--spiders', type=str, nargs='+', choices=['kompas', 'tempo', 'metro', 'republika'], help='Specify sites to crawl. Options are kompas, tempo, metro, republika.')
    parser.add_argument('-d', '--date', type=int, nargs='+', help='Specify dates/years to crawl.') 
    args = parser.parse_args()

    if args.date:
        years = args.date
    else:
        years = []
    if args.spiders:
        spiders = args.spiders
    else:
        spiders = ['republika', 'tempo', 'kompas', 'metro']

    print(spiders)
    print(years)

    c = CrawlerProcess(get_project_settings())
    configure_logging({'LOG_FILE': '/home/cilsat/dev/koran-crawler/output/crawl.log'})

    processes = []
    for spider in spiders:
        if years:
            for year in years:
                p = Process(target=korancrawler, args=(c, spider, year))
                p.start()
                processes.append(p)
        else:
            p = Process(target=korancrawler, args=(c, spider))
            p.start()
            processes.append(p)

    for p in processes:
        p.join()
