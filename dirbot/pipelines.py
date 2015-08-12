from scrapy.exceptions import DropItem
from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals

class FilterWordsPipeline(object):
    """A pipeline for filtering out items which contain certain words in their
    description"""

    # put all words in lowercase
    words_to_filter = []

    def process_item(self, item, spider):
        for word in self.words_to_filter:
            if word in unicode(item['text']).lower():
                raise DropItem("Contains forbidden word: %s" % word)
        else:
            return item

"""
class MultiOutItemPipeline(object):
    SaveTypes = ['xml', 'txt']

    def __init__(self):
        dispatcher.connect(self.spider_opened, signal=signals.spider_opened)
        dispatcher.connect(self.spider_closed, signal=signals.spider_closed)
        
    def spider_opened(self, spider):
        self.files = dict([ (name, open('output/'+name+
"""
