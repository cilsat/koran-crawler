import scrapy
from scrapy.spiders import Spider
from scrapy.selector import Selector
from scrapy.item import Item, Field
from dirbot.items import Art

from newspaper.article import Article
from newspaper.source import Configuration

def buildRepublikaCalendar():
    # calendar subroutine to populate start_urls with dates 
    calendar = []
    tahun = range(2010,2011)
    for t in tahun:
        tstring = str(t) + "/"
        bulan = range(1,13)
        for b in bulan:
            tanggal = []
            if b == 1 or b == 3 or b == 5 or b == 7 or b == 8 or b == 10 or b == 12:
                tanggal = range(1,32)
            elif b == 4 or b == 6 or b == 9 or b == 11:
                tanggal = range(1,31)
            elif (t+2) % 4 == 0:
                tanggal = range(1,30)
            else:
                tanggal = range(1,29)
            
            bstring = ""
            if b < 10:
                bstring = "0" + str(b) + "/"
            else:
                bstring = str(b) + "/"

            for t in tanggal:
                dstring = ""
                if t < 10:
                    dstring = "0" + str(t)
                else:
                    dstring = str(t)

                calendar.append(tstring + bstring + dstring)

    return calendar

class RepublikaSpider(Spider):

    name = "republika"
    allowed_domains = ["republika.co.id"]
    start_urls = ["http://www.republika.co.id/index/" + date for date in buildRepublikaCalendar()]

    def __init__(self):
        # newspaper config
        self.config = Configuration()
        self.config.language = 'id'
        self.config.fetch_images = False
        self.index = 0

    def parse(self, response):

        sel = Selector(response)

        # selects all article urls on page. may need to refine
        urls = sel.xpath('//h4/a/@href').extract()

        # parse subsequent index depths recursively; stops when no article links are found
        if len(urls) > 0:
            new_url = response.url
            print '1' + new_url
            # hardcoded link format for republika
            if len(new_url.split('/')) > 7:
                new_url = new_url.replace(new_url[44:],str(int(new_url[44:]) + 40))
            else:
                new_url += '/' + str(40)

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

