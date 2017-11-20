#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
import requests
import re
import sys
import datetime
import logging
import urllib.parse as urlparse
from lxml import html
from logging.config import fileConfig
from sqlalchemy.orm import subqueryload
from .database.config import session_scope
from .database.model import Market, Product, Config, Origin, Price, Part, Alias
from . import _logging_config_path


fileConfig(_logging_config_path)
log = logging.getLogger(__name__)


class MarketBrowser(object):
    __metaclass__ = abc.ABCMeta

    NUM_RE = re.compile('''
            (?:\d+)
    ''', re.X)

    ERROR_MAP = {
        0: '產品重量單位轉換失敗',
        1: '找不到相對應的品項媒合值',
        2: '定義產品部位輸入無效的字串',
        3: '處理文本{名稱:%s, 重量:%s, 產地:%s, 價格:%s}發生溢位或值錯誤',
        4: '處理文本{%s}發生溢位或值錯誤'
    }

    INFO_MAP = {
        0: '訪問%s以取得所有%s產品',
        1: '無法自動分類產品「%s」，產地%s，請定義產品類型或放棄(Enter)\n%s:',
        2: '將產品%s人工定義為%s',
        3: '放棄定義產品%s',
        4: '將產品%s自動定義為%s'
    }

    ORIGIN_MAP = {
        '臺北': '臺灣', '臺中': '臺灣', '基隆': '臺灣', '臺南': '臺灣', '高雄': '臺灣', '新北': '臺灣', '宜蘭': '臺灣',
        '桃園': '臺灣', '嘉義': '臺灣', '新竹': '臺灣', '苗栗': '臺灣', '南投': '臺灣', '彰化': '臺灣', '雲林': '臺灣',
        '屏東': '臺灣', '花蓮': '臺灣', '臺東': '臺灣', '金門': '臺灣', '澎湖': '臺灣', '臺灣': '臺灣',
        '臺中豐原': '台灣', '屏東里港': '臺灣', '雲林莿桐': '臺灣', '西螺': '臺灣', '臺南佳里': '臺灣',
        '屏東萬丹': '臺灣', '美濃': '臺灣', '臺中大甲': '臺灣', '南投埔里': '臺灣',
        '澳洲': '澳洲',
        '中國': '中國',
        '美國': '美國'
    }

    UNIT_MAP = {
        'KG': (0, 1000), 'G': (1, 1), 'g': (1, 1), 'kg': (0, 1000)
    }

    UNIT_RE = re.compile('''
        (?:
            (?P<kg>\d*.\d+|\d+)(?=KG|kg)
            |
            (?P<g>\d*.\d+|\d+)(?=G|g)
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
            urls = []
            try:
                map_strs = product_map[config.name]
                for map_str in map_strs:
                    urls += self.get_product_urls(map_str)
                yield config, urls
            except KeyError:
                log.error(MarketBrowser.ERROR_MAP[1])

    def direct(self, product_map):
        for config, urls in self.config_generator(product_map):
            for url in urls:
                product, price = self.get_product_price(url)
                if not product and not price:
                    continue
                # return self if not exists
                product = self.check_product(product)
                if not product.id:
                    MarketBrowser.STACK.append((config, product, price))
                elif product.track:
                    price.product = product
                    self.set_price(price)

    @classmethod
    def clear_stack(cls):
        def set_product_price(product, price):
            if product.track:
                price.product = product
                MarketBrowser.set_price(price)
            else:
                MarketBrowser.set_product(product)

        manuals = []

        for config, product, price in cls.STACK:
            product = MarketBrowser.classify_product_auto(config, product)
            if product.part_id:
                set_product_price(product, price)
            else:
                manuals.append((config, product, price))

        for config, product, price in manuals:
            product = MarketBrowser.classify_product_manual(config, product)
            if product.part_id:
                set_product_price(product, price)

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
    def classify_product_auto(config, product):
        for part in config.parts:
            find = False
            if part.name in product.name:
                find = True
            for alias in part.aliases:
                if alias.name in product.name:
                    find = True
            if find:
                product.track = True
                product.part_id = part.id
                log.info(MarketBrowser.INFO_MAP[4] % (product.name, part.name))
                return product
        return product

    @staticmethod
    def classify_product_manual(config, product):
        def decode(s):
            encoding = sys.stdin.encoding
            return s.encode(encoding, 'replace').decode(encoding)

        while True:
            options = ''.join('(%s): %s ' % (i, part.name) for i, part in enumerate(config.parts))
            options = decode(options)
            i = input(MarketBrowser.INFO_MAP[1] % (product.name, product.origin.name, options))

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
                if i in range(config.parts.__len__()):
                    product.part_id = config.parts[i].id
                    product.track = True
                    log.info(MarketBrowser.INFO_MAP[2] % (product.name, config.parts[i].name))
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

    @staticmethod
    def get_origin(origin_str):
        with session_scope() as session:
            try:
                origin_str = MarketBrowser.ORIGIN_MAP[origin_str]
                origin = session.query(Origin).filter(Origin.name == origin_str).first()
            except KeyError:
                origin = session.query(Origin).filter(Origin.name == '其他').first()
            session.expunge(origin)
        return origin

    def __init__(self, market_name):
        self.date = datetime.date.today().strftime('%Y-%m-%d')
        with session_scope() as session:
            self.configs = session.query(Config).options(subqueryload(Config.parts).subqueryload(Part.aliases)).all()
            self.market = session.query(Market).filter(Market.name == market_name).first()
            session.expunge_all()


class Wellcome(MarketBrowser):

    NAME = '頂好'

    PRODUCTS_ROUTE = 'https://sbd-ec.wellcome.com.tw/product/listByCategory/%s?max=1000&query=%s'
    INDEX_ROUTE = 'https://sbd-ec.wellcome.com.tw'

    PRODUCT_MAP = {
        '雞肉': [(12, 13)], '豬肉': [(12, 14)],
        '雜貨': [(31, 35)], '蔬菜': [(7, 8), (7, 9), (7, 10)],
        '水果': [(2, 4), (2, 6)]
    }

    NAME_RE = re.compile('''
            (.*?)\d
    ''', re.X)

    def __init__(self):
        super(Wellcome, self).__init__(Wellcome.NAME)

    @staticmethod
    def get_product_urls(map_str):
        url = Wellcome.PRODUCTS_ROUTE % (map_str[0], map_str[1])
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
            weight_token = MarketBrowser.UNIT_RE.findall(weight_str)
            weight = self.get_weight(weight_token[0])
            pid = MarketBrowser.NUM_RE.findall(url)[-1]
            origin = self.get_origin(origin_str)
            weight = int(weight)
            price = int(price_str)
        except:
            log.error(MarketBrowser.ERROR_MAP[3] % (name_str, weight_str, origin_str, price_str))
            return None, None

        product = Product(name=name, origin=origin, market_id=self.market.id, pid=pid)
        price = Price(price=price, weight=weight, date=self.date)
        return product, price


class Geant(MarketBrowser):

    NAME = '愛買'

    PRODUCTS_ROUTE = 'http://www.gohappy.com.tw/shopping/Browse.do?op=vc&cid=%s&sid=12'
    INDEX_ROUTE = 'http://www.gohappy.com.tw'

    PRODUCT_MAP = {
        '雞肉': ['301299'], '豬肉': ['212375'],
        '雜貨': ['295095'], '蔬菜': ['29979', '358367', '161460&cp=1', '161460&cp=2'],
        '水果': ['208879']
    }

    NAME_RE = re.compile('''
        (?:.+?)(?=\d+.*|$)
    ''', re.X)

    ORIGIN_RE = re.compile('''
           (?<=產地：)(.*?)\W
    ''', re.X)

    COUNT_RE = re.compile('''
           (?<=數量：)(.*?)\W
    ''', re.X)

    WEIGHT_RE = re.compile('''
           (?<=規格：)(.*?)\W
    ''', re.X)

    def __init__(self):
        super(Geant, self).__init__(Geant.NAME)

    @staticmethod
    def get_product_urls(map_str):
        url = Geant.PRODUCTS_ROUTE % (map_str)
        res = requests.get(url)
        parsed_page = html.fromstring(res.content)
        urls = parsed_page.xpath('//ul[@class="product_list"]//h5/a/@href')
        return [Geant.INDEX_ROUTE + url for url in set(urls)]

    def get_product_price(self, url):
        def replace(s):
            return re.sub(r'台', '臺', s)

        res = requests.get(url)
        page = html.fromstring(res.content)
        name_str = ''.join(
                        page.xpath('//div[@class="product_content"]//tr[contains(string(), "商品")]/td[2]//text()')
                    ).strip()
        intro = ''.join(page.xpath('//dd[@class="introduction"]/text()')).strip()
        price_str = ''.join(page.xpath('//dd[@class="list_price"]/text()')).strip()
        try:
            name = ''.join([s for s in name_str if s.isalnum()])
            if not name:
                name = ''.join(page.xpath('//h3[@class="trade_Name"]/text()')).strip()
            name = Geant.NAME_RE.findall(name)[0]
            try:
                origin_str = Geant.ORIGIN_RE.findall(intro)[0]
            except IndexError:
                origin_str = ''.join(
                    page.xpath('//div[@class="product_content"]//tr[contains(string(), "產地")]/td[2]//text()')
                ).strip()
            count_str = Geant.COUNT_RE.findall(intro)[0]
            weight_str = Geant.WEIGHT_RE.findall(intro)[0]
            weight_token = MarketBrowser.UNIT_RE.findall(weight_str)
            count = MarketBrowser.NUM_RE.findall(count_str)[0]
            weight = self.get_weight(weight_token[0])
            pid = urlparse.parse_qs(url)['pid'][0]
            origin_str = replace(origin_str)
            origin = self.get_origin(origin_str)
            weight = int(weight) * int(count)
            price = int(price_str)
        except:
            print(url)
            log.error(MarketBrowser.ERROR_MAP[4] % intro)
            return None, None

        product = Product(name=name, origin=origin, market_id=self.market.id, pid=pid)
        price = Price(price=price, weight=weight, date=self.date)
        return product, price

















