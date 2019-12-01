#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# @Author  : YangTao
# @blog    : https://ytao.top
import base64
import re
import logging
import scrapy
from io import BytesIO
from fontTools.ttLib import TTFont
from scrapy import cmdline,Request
from ytaoCrawl.items import YtaocrawlItem


class YtaoSpider(scrapy.Spider):
    # 定义爬虫名称
    name = "ytaoSpider"
    # 允许爬取的域名，但不包含 start_urls 中的链接
    allowed_domains = ["58.com"]
    # 爬虫链接，不含页码
    target_url = "https://bj.58.com/chuzu/pn"
    # 起始爬取链接
    start_urls = [
        "https://bj.58.com/chuzu/?PGTID=0d100000-0038-e441-0c8a-adeb346199d8&ClickID=2"
    ]

    def download(self, response, fName):
        with open(fName + ".html", 'wb') as f:
            f.write(response.body)

    def pageNum(self, response):
        # 获取分页的 html 代码块
        page_ele = response.xpath("//li[@id='pager_wrap']/div[@class='pager']")
        # 通过正则获取含有页码数字的文本
        num_eles = re.findall(r">\d+<", page_ele.extract()[0].strip())
        # 找出最大的一个
        count = 0
        for num_ele in num_eles:
            num_ele = str(num_ele).replace(">", "").replace("<", "")
            num = int(num_ele)
            if num > count:
                count = num
        return count

    # 避免取xpath解析数据时索引越界
    def xpath_extract(self, selector, index):
        if len(selector.extract()) > index:
            return selector.extract()[index].strip()
        return ""

    def setData(self, response):
        items = []
        houses = response.xpath("//ul[@class='house-list']/li[@class='house-cell']")
        for house in houses:
            item = YtaocrawlItem()
            # 标题
            item["title"] = self.decrypt(response, self.xpath_extract(house.xpath("div[@class='des']/h2/a/text()"), 0))
            # 面积
            item["room"] = self.decrypt(response, self.xpath_extract(house.xpath("div[@class='des']/p[@class='room']/text()"), 0))
            # 位置
            item["position"] = self.decrypt(response, self.xpath_extract(house.xpath("div[@class='des']/p[@class='infor']/a/text()"), 0))
            # 小区
            item["quarters"] = self.decrypt(response, self.xpath_extract(house.xpath("div[@class='des']/p[@class='infor']/a/text()"), 1))
            money = self.xpath_extract(house.xpath("div[@class='list-li-right']/div[@class='money']/b/text()"), 0)
            unit = self.xpath_extract(house.xpath("div[@class='list-li-right']/div[@class='money']/text()"), 1)
            # 价格
            item["price"] = self.decrypt(response, money+unit)
            url = self.xpath_extract(house.xpath("div[@class='des']/h2/a/@href"), 0)
            if url.__contains__("?"): url = url[0:url.index("?")]
            # 租房链接
            item["url"] = self.decrypt(response, url)
            items.append(item)
        return items

    def decrypt(self, response, code):
        secret = re.findall("charset=utf-8;base64,(.*?)'\)", response.text)[0]
        code = self.secretfont(code, secret)
        return code

    def secretfont(self, code, secret):
        # 将字体文件编码转换为 UTF-8 编码的字节对象
        bytes = secret.encode(encoding='UTF-8')
        # base64位解码
        decodebytes = base64.decodebytes(bytes)
        # 利用 decodebytes 初始化 BytesIO，然后使用 TTFont 解析字体库
        font = TTFont(BytesIO(decodebytes))
        # 字体的映射关系
        font_map = font['cmap'].tables[0].ttFont.tables['cmap'].tables[0].cmap
        chars = []
        for char in code:
            # 将每个字符转换成十进制的 ASCII 码
            decode = ord(char)
            # 如果映射关系中存在 ASCII 的 key，那么这个字符就有对应的字体
            if decode in font_map:
                # 获取映射的值
                val = font_map[decode]
                # 根据规律，获取数字部分，再减1得到真正的值
                char = int(re.findall("\d+", val)[0]) - 1
            chars.append(char)
        return "".join(map(lambda s:str(s), chars))

    def parse(self, response):
        items = self.setData(response)
        for item in items:
            yield item

        num = self.pageNum(response)
        # 开始页面本来就是第一页，所以在遍历页面时，过滤掉第一页
        p = 1
        while p < 1:
            p += 1
            try:
                # 拼接下一页链接
                url = self.target_url + str(p)
                # 进行抓取下一页
                yield Request(url, callback=self.parse)
            except BaseException as e:
                logging.error(e)
                print("爬取数据异常：", url)



if __name__ == '__main__':
    name = YtaoSpider.name
    cmd = 'scrapy crawl {0}'.format(name)
    cmdline.execute(cmd.split())
