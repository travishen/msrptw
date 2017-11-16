#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
import requests
import re
from lxml import html
from .database.config import session_scope
from sqlalchemy.orm import subqueryload
from .database.model import Market, Product, Config, Origin


class MarketBrowser(object):
    __metaclass__ = abc.ABCMeta

    NUM_RE = re.compile('''
            (?=\d+)
        ''')

    @abc.abstractstaticmethod
    def get_product_urls(map_str):
        return

    @abc.abstractmethod
    def init_product(self):
        return

    def config_generator(self, product_map):
        for config in self.configs:
            try:
                map_str = product_map[config.name]
                urls = self.get_product_urls(map_str)
                yield config, urls
            except KeyError:
                print('missing map value for %s.' % config.name)

    def direct(self, product_map):
        for config, urls in self.config_generator(product_map):
            for url in urls:
                product = self.init_product(url)
                if not self.check_product(product):
                    product = self.classify_product(config, product)

    @staticmethod
    def set_product(product):
        with session_scope() as session:
            session.add(product)

    @staticmethod
    def classify_product(config, product):
        while True:
            options = config.parts_to_dict()
            i = input('We find this new product %s, please helping us classify it. \n%s:' % (product.name, options))
            if i in range(len(options)):
                product.part = config.parts[i]
                break
        return product

    @staticmethod
    def check_product(product):
        with session_scope() as session:
            return session.query(Product).filter(Product.pid == product.pid).count() > 0

    def get_origin(self, origin_map, origin):
        return self.origins.filter(Origin.name == origin_map[origin])

    def __init__(self):
        with session_scope() as session:
            self.configs = session.query(Config).options(subqueryload(Config.parts)).all()
            self.origins = session.query(Origin).all()
            session.expunge_all()


class Wellcome(MarketBrowser):

    PRODUCTS_ROUTE = 'https://sbd-ec.wellcome.com.tw/product/listByCategory/12?query=%s'
    INDEX_ROUTE = 'https://sbd-ec.wellcome.com.tw'

    PRODUCT_MAP = {
        '雞肉': '12', '豬肉': '13'
    }

    ORIGIN_MAP = {
        '臺灣': '臺灣', '澳洲': '澳洲'
    }

    NAME_RE = re.compile('''
            (?=.+\d)
        ''')

    UNIT = 'g'

    def __init__(self):
        super(Wellcome, self).__init__()

    @staticmethod
    def get_product_urls(map_str):
        url = Wellcome.PRODUCTS_ROUTE % map_str
        res = requests.get(url)
        parsed_page = html.fromstring(res.content)
        return [Wellcome.INDEX_ROUTE + url for url in parsed_page.xpath('//div[@class="item-name"]/a/@href')]

    def init_product(self, url):

        res = requests.get(url)
        parsed_page = html.fromstring(res.content)
        name = parsed_page.xpath('//div[@class="product-name"]/text()')
        gram = parsed_page.xpath('//ul[@class="product-list"]/li[3]/text()')
        origin = parsed_page.xpath('//ul[@class="product-list"]/li[2]/text()')

        name = Wellcome.NAME_RE.findall(name)[0]
        gram = MarketBrowser.NUM_RE.findall(gram)[0]
        pid = MarketBrowser.NUM_RE.findall(url)[-1]
        origin_ins = self.get_origin(Wellcome.ORIGIN_MAP, origin)
        origin_id = origin_ins.id

        return Product(name=name, origin_id=origin_id, gram=gram, pid=pid)















