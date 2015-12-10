
import scrapy
from scrapy.spiders import Spider
from scrapy.selector import Selector
from scrapy.item import Item, Field
from dirbot.items import Art

from newspaper.article import Article
from newspaper.source import Configuration
from newspaper import nlp


class MetroSpider(Spider):

    name = "metro"
    allowed_domains = ["metrotvnews.com"]

    def __init__(self, date=None):
        # newspaper config
        self.config = Configuration()
        self.config.language = 'id'
        self.memoize_articles = False
        self.config.fetch_images = False
        self.year = None
        self.date = None

        print "Date: " + str(date)

        if date:
            if len(date) == 4:
                self.year = date
            if len(date) == 8:
                self.date = date
        else:
            import time
            self.today = time.strftime("%Y/%m/%d/")

    def start_requests(self):
        # categories: "news" 6, "jatim" 171, "jabar" 174, "jateng" 177, "internasional" 40
        # "ekonomi" 7, "bola" 8, "olahraga" 9, "teknologi" 52, "otomotif" 11, "hiburan" 10
        # "rona" 160
        categories = ["6", "171", "174", "177", "40", "7", "8", "9", "52", "11", "10", "160"]

        for date in self.generateIndex():
            for category in categories:
                yield scrapy.Request("http://www.metrotvnews.com/index/" + date + category, self.parse)

    def parse(self, response):

        sel = Selector(response)

        # selects all article urls on page. may need to refine
        urls = sel.xpath('//div/h4/a/@href').extract()

        # parse subsequent index depths recursively; stops when no article links are found
        if urls:
            new_url = response.url
            # hardcoded link format for multipage index in metro
            slash_split = new_url.split('/')
            if len(slash_split) > 8:
                next_page = '/' + str(int(slash_split[-1]) + 30)
                new_url = '/'.join(slash_split[:-1]) + next_page
            else:
                new_url += '/' + str(30)

            print new_url

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
        item['url'] = article.url
        item['text'] = '\n'.join(nlp.split_sentences(article.text))
        yield item

    def generateIndex(self):
        # calendar subroutine to populate start_urls with dates 
        calendar = []
        if self.year:
            tstring = self.year
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

                    calendar.append(tstring + '/' + bstring + '/' + dstring + "/")

        elif self.date:
            year = self.date[-4:]
            month = self.date[2:4]
            day = self.date[:2]
            calendar = [year + "/" + month + "/" + day + "/"]

        elif self.today:
            calendar = [self.today]

        return calendar
