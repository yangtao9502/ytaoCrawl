# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html
import random

import logging
from scrapy import signals

from ytaoCrawl import settings


class YtaocrawlSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class YtaocrawlDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class RandomUserAgentMiddleware(object):
    def __init__(self, agents):
        self.agent = agents

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            agents=crawler.settings.get('USER_AGENT')
        )

    def process_request(self, request, spider):
        # 随机获取设置中的一个 User-Agent
        request.headers.setdefault('User-Agent', random.choice(self.agent))

class ProxyIPMiddleware(object):
    def __init__(self, ip=''):
        self.ip = ip

    def process_request(self, request, spider):
        # 如果当前的地址重定向到了验证码地址,就使用代理ip进行重新请求
        if self.ban_url(request.url):
            # 获取被重定向的地址
            redirect_urls = request.meta.get("redirect_urls")[0]
            # 将当前重定向到验证码的地址改为原始请求地址
            request._set_url(redirect_urls)
            # 设置动态代理,这里在线上一般使用接口动态生成代理
            request.meta["proxy"] = "http://%s" % (self.proxy_ip())

    def ban_url(self, url):
        # settings中设置的验证码或被禁止的页面链接
        dic = settings.BAN_URLS
        # 验证当前请求地址是否为验证码地址
        for d in dic:
            if url.find(d) != -1:
                return True
        return False

    # 代理动态生成的 ip:port
    def proxy_ip(self):
        # 模拟动态生成代理地址
        ips = [
            "127.0.0.1:8888",
            "127.0.0.1:8889",
        ]
        return random.choice(ips);

    def process_response(self, request, response, spider):
        # 如果不是成功响应,则重新爬虫
        if response.status != 200:
            logging.error("失败响应: "+ str(response.status))
            return request
        return response
