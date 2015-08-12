import os
import scrapy
from scrapy.spiders import Spider
from scrapy.selector import Selector
from scrapy.item import Item, Field
from dirbot.items import Art

from newspaper.article import Article
from newspaper.source import Configuration
#from newspaper import nlp

class TempoSpider(Spider):

    name = "tempo"
    allowed_domains = ["tempo.co"]

    def __init__(self, year=None):
        # newspaper config
        self.config = Configuration()
        self.config.language = 'id'
        self.config.fetch_images = False

        # input argument to define year
        self.year = year

        # container for all sentences
        self.sentences = []

        self.curpath = os.path.abspath(__file__)
        self.datpath = os.path.join(self.curpath, '/output/' + self.name + '/')
        self.datfile = os.path.join(self.datpath, self.name + '-' + self.year + '.txt')

    def start_requests(self):
        # yield requests for all days in the given year
        for date in self.buildTempoCalendar():
            yield scrapy.Request("http://www.tempo.co/indeks/" + date, self.parse)

    def parse(self, response):
        sel = Selector(response)

        # selects all article urls on page. may need to refine. tempo doesn't employ index pagination
        urls = sel.xpath('//ul/li/div/h3/a/@href').extract()

        # pool article downloads and offload parsing to newspaper
        for url in urls:
            print url
            yield scrapy.Request(response.urljoin(url), callback=self.parse_article)

    def parse_article(self, response):
        # utilize newspaper for article parsing
        article = Article(url=response.url, config=self.config)
        article.set_html(response.body)
        article.parse()

        #self.sentences.append(nlp.split_sentences(article.text))
        
        item = Art()
        item['title'] = article.title
        item['url'] = article.url
        item['text'] = article.text
        yield item

    def buildTempoCalendar(self):
        # calendar subroutine to populate start_urls with dates 
        calendar = []
        bulan = range(1,13)
        tstring = self.year + "/"

        for b in bulan:
            tanggal = []
            if b == 1 or b == 3 or b == 5 or b == 7 or b == 8 or b == 10 or b == 12:
                tanggal = range(1,32)
            elif b == 4 or b == 6 or b == 9 or b == 11:
                tanggal = range(1,31)
            elif b == 2 and (int(self.year)+2) % 4 == 0:
                tanggal = range(1,30) 
            elif b == 2 :
                tanggal = range(1,29)
            
            bstring = ""
            if b < 10:
                bstring = "0" + str(b) + "/"
            else:
                bstring = str(b) + "/"

            for t in tanggal:
                dstring = ""
                if t < 10:
                    dstring = "0" + str(t) + "/"
                else:
                    dstring = str(t) + "/"

                calendar.append(tstring + bstring + dstring)

        return calendar
