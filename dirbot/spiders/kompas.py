import scrapy
from scrapy.spiders import Spider
from scrapy.selector import Selector
from scrapy.item import Item, Field
from dirbot.items import Art

from newspaper.article import Article
from newspaper.source import Configuration


class KompasSpider(Spider):

    name = "kompas"
    allowed_domains = ["kompas.com"]

    def __init__(self, year=None):
        # newspaper config
        self.config = Configuration()
        self.config.language = 'id'
        self.config.fetch_images = False
        self.year = year

    def start_requests(self):
        categories = ["nasional", "regional", "megapolitan", "internasional", "olahraga", "sains", "edukasi", "ekonomi", "bola", "tekno", "entertainment", "otomotif", "health", "female", "properti", "travel"]

        for date in self.buildKompasCalendar():
            for category in categories:
                yield scrapy.Request("http://indeks.kompas.com/indeks/index/" + category + "?" + date, self.parse)        

    def parse(self, response):

        sel = Selector(response)

        # selects all article urls in kompas index page. may need to refine
        urls = sel.xpath('//div/ul/li/div/h3/a/@href').extract()

        # parse subsequent index depths recursively; stops when no article links are found
        if len(urls) > 0:
            new_url = response.url
            print '1' + new_url
            # hardcoded link format for kompas
            if len(new_url.split('&')) < 2:
                s = new_url.find('?p=')
                new_url = new_url.replace(new_url[s+3:], str(int(new_url[s+3:])+1))
            else:
                new_url = new_url.split('?')[0] + '?p=2'

            print '2' + new_url
            yield scrapy.Request(new_url, callback=self.parse)

            # pool article downloads and offload parsing to newspaper
            for url in urls:
                yield scrapy.Request(url, callback=self.parse_article)

    def parse_article(self, response):
        # utilize newspaper for article parsing
        article = Article(url=response.url, config=self.config)
        article.set_html(response.body)

        article.parse()
        item = Art()
        item['title'] = article.title
        item['authors'] = article.authors
        item['url'] = article.url
        item['text'] = article.text
        yield item

    def buildKompasCalendar(self):
        # calendar subroutine to populate start_urls with dates 
        calendar = []
        tstring = str(self.year)
        bulan = range(1,13)

        for b in bulan:
            tanggal = []
            if b == 1 or b == 3 or b == 5 or b == 7 or b == 8 or b == 10 or b == 12:
                tanggal = range(1,32)
            elif b == 4 or b == 6 or b == 9 or b == 11:
                tanggal = range(1,31)
            elif (int(self.year)+2) % 4 == 0:
                tanggal = range(1,30)
            else:
                tanggal = range(1,29)
            
            bstring = ""
            if b < 10:
                bstring = "0" + str(b)
            else:
                bstring = str(b)

            for t in tanggal:
                dstring = ""
                if t < 10:
                    dstring = "0" + str(t)
                else:
                    dstring = str(t)

                calendar.append("&tanggal=" + dstring + "&bulan=" + bstring + "&tahun=" + tstring)

        return calendar
