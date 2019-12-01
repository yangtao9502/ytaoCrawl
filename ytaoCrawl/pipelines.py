# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import uuid
from ytaoCrawl.utils.mysqlUtils import insert, select, delete_by_id


class YtaocrawlPipeline(object):

    def process_item(self, item, spider):
        table = "crawl"
        item["id"] = str(uuid.uuid1())
        # 如果当前爬取信息的链接在库中有存在，那么就删除旧的再保存新的
        list = select(str.format("select * from {0} WHERE url = '{1}'", table, item["url"]))
        if len(list) > 0:
            for o in list:
                delete_by_id(o[0], table)
        insert(item, "crawl")
        return item
