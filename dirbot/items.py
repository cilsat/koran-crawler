from scrapy.item import Item, Field


class Website(Item):

    name = Field()
    description = Field()
    url = Field()

class Art(Item):
    title = Field()
    authors = Field()
    url = Field()
    text = Field()
