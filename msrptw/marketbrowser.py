#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
import requests
import re
import sys
import datetime
import logging
from lxml import html
from logging.config import fileConfig
from sqlalchemy.orm import subqueryload
from .database.config import session_scope
from .database.model import Market, Product, Config, Origin, Price
from . import _logging_config_path

fileConfig(_logging_config_path)
log = logging.getLogger(__name__)


class MarketBrowser(object):
    __metaclass__ = abc.ABCMeta

    NUM_RE = re.compile('''
            (\d+)
    ''', re.X)

    ERROR_MAP = {
        0: '產品重量單位轉換失敗',
        1: '找不到相對應的品項媒合值',
        2: '定義產品部位輸入無效的字串',
        3: '處理文本(名稱:%s, 重量:%s, 產地:%s, 價格:%s)發生溢位或值錯誤'
    }

    INFO_MAP = {
        0: '訪問%s以取得所有%s產品',
        1: '在%s超市發現新產品「%s」，請定義產品類型或放棄(Enter)\n%s:',
        2: '將產品%s定義為%s',
        3: '放棄定義產品%s'
    }

    ORIGIN_MAP = {
        '臺灣': '台灣', '澳洲': '澳洲',
    }

    UNIT_MAP = {
        'KG': (0, 1000), 'G': (1, 1)
    }

    UNIT_RE = re.compile('''
        (?:
            (?P<kg>.*)KG | (?P<g>.*)G
        )
    ''', re.X)

    STACK = []

    @abc.abstractstaticmethod
    def get_product_urls(self):
        return

    @abc.abstractmethod
    def get_product_price(self):
        return

    def config_generator(self, product_map):
        for config in self.configs:
            log.info(MarketBrowser.INFO_MAP[0] % (self.market.name, config.name))
            try:
                map_str = product_map[config.name]
                urls = self.get_product_urls(map_str)
                yield config, urls
            except KeyError:
                log.error(MarketBrowser.ERROR_MAP[1])

    def direct(self, product_map):
        for config, urls in self.config_generator(product_map):
            for url in urls:
                product, price = self.get_product_price(url)
                # return self if not exists
                product = self.check_product(product)
                if not product.id:
                    MarketBrowser.STACK.append((self.market, config, product, price))
                elif product.track:
                    price.product = product
                    self.set_price(price)

    @classmethod
    def clear_stack(cls):
        for market, config, product, price in cls.STACK:
            product = MarketBrowser.classify_product(market, config, product)
            if product.track:
                price.product = product
                MarketBrowser.set_price(price)
            else:
                MarketBrowser.set_product(product)
        cls.STACK = []

    @staticmethod
    def set_product(product):
        with session_scope() as session:
            session.add(product)

    @classmethod
    def get_weight(cls, token):
        for index, multiplier in cls.UNIT_MAP.values():
            unit_value = token[index]
            if unit_value:
                try:
                    unit_value = float(unit_value)
                except ValueError:
                    log.error(MarketBrowser.ERROR_MAP[0])
                    return None
                return unit_value * multiplier

    @staticmethod
    def classify_product(market, config, product):
        def decode(s):
            encoding = sys.stdin.encoding
            return s.encode(encoding, 'replace').decode(encoding)

        while True:
            options = ''.join('(%s): %s ' % (i, part.name) for i, part in enumerate(config.parts))
            options = decode(options)
            i = input(MarketBrowser.INFO_MAP[1] % (market.name, product.name, options))

            if not i:
                log.info(MarketBrowser.INFO_MAP[3] % product.name)
                product.track = False
                break
            else:
                try:
                    i = int(i)
                except ValueError:
                    log.error(MarketBrowser.ERROR_MAP[2])
                    continue
                if i in range(config.parts.__len__() + 1):
                    selected_config = config.parts[i]
                    product.part_id = selected_config.id
                    product.track = True
                    log.info(MarketBrowser.INFO_MAP[2] % (product.name, selected_config.name))
                    break
        return product

    @staticmethod
    def check_product(product):
        with session_scope() as session:
            db_product = session.query(Product).filter(Product.pid == product.pid).filter(Product.market_id == product.market_id).first()
            if db_product:
                # update product here  if needed
                session.expunge(db_product)
                return db_product
            return product

    @staticmethod
    def set_price(price):
        with session_scope() as session:
            db_price = session.query(Price).filter(Price.date == price.date).filter(Price.product_id == price.product.id).first()
            if db_price:
                db_price.price = price.price
                db_price.weight = price.weight
            else:
                session.add(price)

    def get_origin(self, origin_str):
        return [o for o in self.origins if o.name == MarketBrowser.ORIGIN_MAP[origin_str]]

    def __init__(self, market_name):
        self.date = datetime.date.today().strftime('%Y-%m-%d')
        with session_scope() as session:
            self.configs = session.query(Config).options(subqueryload(Config.parts)).all()
            self.origins = session.query(Origin).all()
            self.market = session.query(Market).filter(Market.name == market_name).first()
            session.expunge_all()


class Wellcome(MarketBrowser):

    NAME = '頂好'

    PRODUCTS_ROUTE = 'https://sbd-ec.wellcome.com.tw/product/listByCategory/12?query=%s'
    INDEX_ROUTE = 'https://sbd-ec.wellcome.com.tw'

    PRODUCT_MAP = {
        '雞肉': '13', '豬肉': '14'
    }

    NAME_RE = re.compile('''
            (.*?)\d
    ''', re.X)

    def __init__(self):
        super(Wellcome, self).__init__(Wellcome.NAME)

    @staticmethod
    def get_product_urls(map_str):
        url = Wellcome.PRODUCTS_ROUTE % map_str
        res = requests.get(url)
        parsed_page = html.fromstring(res.content)
        urls = parsed_page.xpath('//div[@class="item-name"]/a/@href')
        return [Wellcome.INDEX_ROUTE + url for url in set(urls)]

    def get_product_price(self, url):
        res = requests.get(url)
        page = html.fromstring(res.content)
        name_str = ''.join(page.xpath('//div[@class="product-name"]/text()')).strip()
        weight_str = ''.join(page.xpath('//ul[@class="product-list"]/li[3]/text()')).strip()
        origin_str = ''.join(page.xpath('//ul[@class="product-list"]/li[2]/text()')).strip()
        price_str = ''.join(page.xpath('//span[@class="item-price"]/text()')).strip()

        try:
            name = Wellcome.NAME_RE.findall(name_str)[0]
            weight_token = Wellcome.UNIT_RE.findall(weight_str)
            weight = self.get_weight(weight_token[0])
            pid = MarketBrowser.NUM_RE.findall(url)[-1]
            origin_ins = self.get_origin(origin_str)[0]
            weight = int(weight)
            price = int(price_str)
        except:
            log.error(MarketBrowser.ERROR_MAP[3] % (name_str, weight_str, origin_str, price_str))
            return None

        origin_id = origin_ins.id

        product = Product(name=name, origin_id=origin_id, market_id=self.market.id, pid=pid)
        price = Price(price=price, weight=weight, date=self.date)
        return product, price

















