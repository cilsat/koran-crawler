import scrapy
from scrapy.spiders import Spider
from scrapy.selector import Selector
from scrapy.item import Item, Field
from dirbot.items import Art

from newspaper.article import Article
from newspaper.source import Configuration

def buildTempoCalendar():
    # calendar subroutine to populate start_urls with dates 
    calendar = []
    bulan = range(1,13)
    for b in bulan:
        tanggal = []
        if b == 1 or b == 3 or b == 5 or b == 7 or b == 8 or b == 10 or b == 12:
            tanggal = range(1,32)
        elif b == 4 or b == 6 or b == 9 or b == 11:
            tanggal = range(1,31)
        else:
            tanggal = range(1,29)
        
        bstring = ""
        if b < 10:
            bstring = "0" + str(b) + "/"
        else:
            bstring = str(b) + "/"

        for t in tanggal:
            tstring = ""
            if t < 10:
                tstring = "0" + str(t) + "/"
            else:
                tstring = str(t) + "/"

            calendar.append(bstring + tstring)

    return calendar

class TempoSpider(Spider):

    name = "tempo"
    allowed_domains = ["tempo.co"]
    start_urls = ["http://www.tempo.co/indeks/2013/" + date for date in buildTempoCalendar()]

    def __init__(self):
        # newspaper config
        self.config = Configuration()
        self.config.language = 'id'
        self.config.fetch_images = False
        self.calendar = buildTempoCalendar()

    def parse(self, response):

        sel = Selector(response)

        # selects all article urls on page. may need to refine
        urls = sel.xpath('//ul/li/div/h3/a/@href').extract()

        # pool article downloads and offload parsing to newspaper
        for url in urls:
            yield scrapy.Request(url, callback=self.parse_article)

    def parse_article(self, response):
        article = Article(response.url, self.config)
        article.html = response.body

        article.parse()
        item = Art()
        item['title'] = article.title
        item['authors'] = article.authors
        item['url'] = article.url
        item['text'] = article.text
        yield item

