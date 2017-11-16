#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
import requests
import re
from lxml import html
from .database.model import Market, Product


class Spider(object):
    __metaclass__ = abc.ABCMeta

    NUM_RE = re.compile('''
            (?=\d+)
        ''')

    @abc.abstractmethod
    def get_products_url(self, **options):
        return

    @abc.abstractmethod
    def set_products(self):
        return


class Wellcome(Spider):

    ROUTE = 'https://sbd-ec.wellcome.com.tw/product/listByCategory/12?query=%'

    CHICKEN = 13
    PORK = 14

    UNIT = 'g'

    def __init__(self, market):
        self.market = market

    @staticmethod
    def get_products_url(self, config):
        url = Wellcome.ROUTE % config
        res = requests.get(url)
        parsed_page = html.fromstring(res.content)
        return parsed_page.xpath('//div[@class="item-name"]/a/@href')

    def set_products(self, url):
        res = requests.get(url)
        parsed_page = html.fromstring(res.content)
        name = parsed_page.xpath('//div[@class="product-name"]/@text')
        gram = parsed_page.xpath('//ul[@class="product-list"]/li[3]/@text')
        origin = parsed_page.xpath('//ul[@class="product-list"]/li[2]/@text')

        try:
            gram = Spider.NUM_RE.findall(gram)[0]
            pid = Spider.NUM_RE.findall(url)[-1]
        except IndexError:
            return None















