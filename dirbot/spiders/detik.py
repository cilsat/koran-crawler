import os
import scrapy
from scrapy.spiders import Spider
from scrapy.selector import Selector
from scrapy.item import Item, Field
from scrapy.http import FormRequest
from dirbot.items import Art

from newspaper.article import Article
from newspaper.source import Configuration
from newspaper import nlp

class DetikSpider(Spider):

    name = "detik"
    allowed_domains = ["detik.com"]
    start_urls = ["http://news.detik.com/indeks"]

    def __init__(self, date=None):
        # newspaper config
        self.config = Configuration()
        self.config.language = 'id'
        self.config.fetch_images = False
        self.year = None
        self.date = None

        # input argument to define year
        # if year is unspecified get the current date
        if date:
            if len(date) == 4:
                self.year = date
            elif len(date) == 8:
                self.date = date

        # container for all sentences
        self.sentences = []

        self.curpath = os.path.abspath(__file__)
        self.datpath = os.path.join(self.curpath, '/output/' + self.name + '/')

    def start_requests(self):
        # yield requests for all days in the given year if "year" argument is given
        # else yield requests for current date
        if self.year or self.date:
            for date in self.generateIndex():
                yield scrapy.Request("http://news.detik.com/indeks/" + date, self.parse)

        else:
            print "ini loh"
            yield scrapy.Request("http://www.tempo.co/indeks/", self.parse)

    def parse(self, response):
        sel = Selector(response)

        # selects all article urls on page. may need to refine. tempo doesn't employ index pagination
        urls = sel.xpath('//ul/li/div/h3/a/@href').extract()
        print str(len(urls)) + " " + response.url

        # pool article downloads and offload parsing to newspaper
        if len(urls) > 1:
            for url in urls:
                print url
                yield scrapy.Request(url, callback=self.parse_article)

    def parse_article(self, response):
        if len(response.body) > 0:
            # utilize newspaper for article parsing
            article = Article(url=response.url, config=self.config)
            article.set_html(response.body)
            article.parse()

            #self.sentences.append(nlp.split_sentences(article.text))

            item = Art()
            item['title'] = article.title
            item['url'] = article.url
            item['text'] = '\n'.join(nlp.split_sentences(article.text.replace('\n', ' ')))
            yield item
        else:
            print response.url + ' DEAD LINK'

    def generateIndex(self):
        # calendar subroutine to populate start_urls with dates
        calendar = []
        if self.year:
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

        elif self.date:
            year = self.date[-4:]
            month = self.date[2:4]
            day = self.date[:2]
            calendar = year + "/" + month + "/" + day + "/"

        return calendar
