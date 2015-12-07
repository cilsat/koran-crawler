import scrapy
from scrapy.spiders import Spider
from scrapy.selector import Selector
from scrapy.item import Item, Field
from dirbot.items import Art

from newspaper.article import Article
from newspaper.source import Configuration
from newspaper import nlp


class KompasSpider(Spider):

    name = "kompas"
    allowed_domains = ["kompas.com"]

    """
    Initialization with "date" argument is meant to ease crawling:
    - No date will crawl today's date
    - A string of date+month+year, eg. "31122014" will crawl a particular date
    - A string of year, eg. "2014" will return all results in that year
    """
    def __init__(self, date=None):
        # newspaper config
        self.config = Configuration()
        self.config.language = 'id'
        self.config.fetch_images = False
        self.year = None
        self.date = None
        self.today = None

        if date:
            if len(date) == 4:
                self.year = date
            elif len(date) == 8:
                self.date = date
        else:
            import time
            self.today = time.strftime("%d %m %Y")

    """
    We request all category index pages
    If cookies are used we also pass a unique cookie name for that category
    and date.
    Subsequent page depths will use this cookie
    """
    def start_requests(self):
        categories = ["news/nasional", "news/regional", "news/megapolitan", "news/internasional", "news/olahraga", "news/sains", "news/edukasi", "ekonomi", "bola", "tekno", "entertainment", "otomotif", "health", "female", "properti", "travel"]

        for date in self.generateIndex():
            day, month, year = date
            for category in categories:
                yield scrapy.Request("http://indeks.kompas.com/indeks/index/" + category + "?&tanggal=" + day + "&bulan=" + month + "&tahun=" + year + "&pos=indeks", meta={'cookiejar': category+'-'+day+month+year}, callback=self.parse_index)

    """
    This function needs to be tailored to the structure of the index of the site you want to crawl.
    """
    def parse_index(self, response):

        sel = Selector(response)

        # this is the xpath function to obtain the url links to articles on an index page
        urls = sel.xpath('//div/ul/li/div/h3/a/@href').extract()

        # if currrent index page has links to articles: stop condition
        if urls:
            new_url = response.url

            # recursively request next index page by adding '1' to current page
            split = new_url.split('=')
            if len(split) == 2:
                next_page = str(int(split[-1])+ 1)
                new_url = split[0] + '=' + next_page
            # start condition
            else:
                category = response.meta['cookiejar'].split('-')[0]
                new_url = "http://indeks.kompas.com/indeks/index/" + category + "?p=2"

            # recursively scrape subsequent index pages
            print "URL Cookie: " + str(response.meta['cookiejar'])
            print "URL: " + new_url
            yield scrapy.Request(new_url, meta = {'cookiejar': response.meta['cookiejar']}, callback=self.parse_index)

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
        item['text'] = '\n'.join(nlp.split_sentences(article.text.replace('\n', ' ')))
        yield item

    def generateIndex(self):
        # calendar subroutine to populate start_urls with dates 
        calendar = []
        if self.year:
            year = str(self.year)
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
                
                month = ""
                if b < 10:
                    month = "0" + str(b)
                else:
                    month = str(b)

                for t in tanggal:
                    day = ""
                    if t < 10:
                        day = "0" + str(t)
                    else:
                        day = str(t)

                    calendar += [day, month, year]
        
        elif self.date:
            year = self.date[-4:]
            month = self.date[2:4]
            day = self.date[:2]
            calendar = [[day, month, year]]

        elif self.today:
            day, month, year = self.today.split()
            calendar = [[day, month, year]]

        print calendar

        return calendar
