# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class YtaocrawlItem(scrapy.Item):
    id = scrapy.Field()
    title = scrapy.Field()
    room = scrapy.Field()
    position = scrapy.Field()
    quarters = scrapy.Field()
    price = scrapy.Field()
    url = scrapy.Field()