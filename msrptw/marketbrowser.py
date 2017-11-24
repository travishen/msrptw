#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
import abc
import requests
import re
import json
import logging
import urllib.parse as urlparse
from lxml import html
from logging.config import fileConfig
from pathos.pools import _ThreadPool
from pathos.multiprocessing import cpu_count
from .database.model import Product, Price
from . import _logging_config_path
from .directory import Directory


fileConfig(_logging_config_path)
log = logging.getLogger(__name__)


class MarketBrowser(Directory):
    """Get all urls from products page with abstract method get_product_urls,
    and browse each product with get_product_price method for getting Product
    and Price instance and do further with Directory methods"""
    __metaclass__ = abc.ABCMeta

    @abc.abstractstaticmethod
    def get_product_urls(self):
        return

    @abc.abstractmethod
    def get_product_price(self):
        return

    def config_generator(self):
        for config in self.configs:
            log.info(MarketBrowser.INFO_MAP[0] % (self.market.name, config.name))
            urls = []
            try:
                map_strs = self.PRODUCT_MAP[config.name]
                for map_str in map_strs:
                    urls += self.get_product_urls(map_str)
                yield config, urls
            except KeyError:
                log.error(Directory.ERROR_MAP[1] % config.name)

    def direct(self):

        def browse_each(config, url):
            product, price = self.get_product_price(url)
            if not product and not price:
                return
            # return self if not exists
            product = self.check_product(product)
            if not product.id:
                Directory.STACK.append((config, product, price))
            elif product.part_id:
                price.product = product
                self.set_price(price)
            return

        cpu = cpu_count()
        pool = _ThreadPool(cpu)
        for c, urls in self.config_generator():
            for u in urls:
                pool.apply_async(browse_each, args=(c, u))
        pool.close()
        pool.join()

    @staticmethod
    def get_html(url):
        try:
            res = requests.get(url, timeout=30)
            parsed_page = html.fromstring(res.content)
        except requests.exceptions.Timeout:
            log.error(Directory.ERROR_MAP[4] % url)
            return html.Element('html')
        except:
            return html.Element('html')

        return parsed_page


class WellcomeBrowser(MarketBrowser):

    NAME = '頂好'

    PRODUCTS_ROUTE = 'https://sbd-ec.wellcome.com.tw/product/listByCategory/%s?max=1000&query=%s'
    INDEX_ROUTE = 'https://sbd-ec.wellcome.com.tw'

    PRODUCT_MAP = {
        '雞肉': [(12, 13)], '豬肉': [(12, 14), (12, 17)],
        '雜貨': [(31, 35)], '蔬菜': [(7, 8), (7, 9), (7, 10)],
        '水果': [(2, 4), (2, 6)]
    }

    NAME_RE = re.compile('''
            (.*?)\d
    ''', re.X)

    def __init__(self):
        super(WellcomeBrowser, self).__init__()

    @staticmethod
    def get_product_urls(map_str):
        url = WellcomeBrowser.PRODUCTS_ROUTE % (map_str[0], map_str[1])
        page = MarketBrowser.get_html(url)
        urls = page.xpath('//div[@class="item-name"]/a/@href')
        return [WellcomeBrowser.INDEX_ROUTE + url for url in set(urls)]

    def get_product_price(self, url):
        page = MarketBrowser.get_html(url)
        name_str = ''.join(page.xpath('//div[@class="product-name"]/text()')).strip()
        weight_str = ''.join(page.xpath('//ul[@class="product-list"]/li[3]/text()')).strip()
        origin_str = ''.join(page.xpath('//ul[@class="product-list"]/li[2]/text()')).strip()
        price_str = ''.join(page.xpath('//span[@class="item-price"]/text()')).strip()

        try:
            name = WellcomeBrowser.NAME_RE.findall(name_str)[0]
            weight = self.get_weight(weight_str)
            pid = Directory.NUM_RE.findall(url)[-1]
            origin = self.get_origin(origin_str)
            weight = int(weight)
            price = int(price_str)
        except:
            log.error(Directory.ERROR_MAP[3] % (name_str, url))
            return None, None

        product = Product(source=WellcomeBrowser.INDEX_ROUTE,
                          name=name, origin=origin,
                          market_id=self.market.id,
                          pid=pid, weight=weight)

        price = Price(price=price, date=self.date)

        return product, price


class GeantBrowser(MarketBrowser):

    NAME = '愛買'

    PRODUCTS_ROUTE = 'http://www.gohappy.com.tw/shopping/Browse.do?op=vc&cid=%s&sid=12'
    INDEX_ROUTE = 'http://www.gohappy.com.tw'

    PRODUCT_MAP = {
        '雞肉': ['301299'], '豬肉': ['212375'],
        '雜貨': ['295095'], '蔬菜': ['29979', '358367', '161460&cp=1', '161460&cp=2', '215204', '161755'],
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
        super(GeantBrowser, self).__init__()

    @staticmethod
    def get_product_urls(map_str):
        url = GeantBrowser.PRODUCTS_ROUTE % (map_str)
        page = MarketBrowser.get_html(url)
        urls = page.xpath('//ul[@class="product_list"]//h5/a/@href')
        return [GeantBrowser.INDEX_ROUTE + url for url in set(urls)]

    def get_product_price(self, url):
        page = MarketBrowser.get_html(url)
        name_str = ''.join(page.xpath('''
            //div[@class="product_content"]//tr[contains(string(), "商品")]/td[2]//text()
        ''')).strip()
        name_str2 = ''.join(page.xpath('//h3[@class="trade_Name"]/text()')).strip()
        intro_str = ''.join(page.xpath('//dd[@class="introduction"]/text()')).strip()
        price_str = ''.join(page.xpath('//dd[@class="list_price"]/text()')).strip()
        try:
            name = ''.join([s for s in name_str if s.isalnum()])
            if not name:
                name = name_str2
            name = GeantBrowser.NAME_RE.findall(name)[0]

            try:
                origin_str = GeantBrowser.ORIGIN_RE.findall(intro_str)[0]
            except IndexError:
                origin_str = ''.join(page.xpath('''
                    //div[@class="product_content"]//tr[contains(string(), "產地")]/td[2]//text()
                ''')).strip()

            try:
                count_str = GeantBrowser.COUNT_RE.findall(intro_str)[0]
                count = Directory.NUM_RE.findall(count_str)[0]
            except IndexError:
                count = 1

            try:
                weight_str = GeantBrowser.WEIGHT_RE.findall(intro_str)[0]
            except:
                weight_str = name_str2

            weight = self.get_weight(weight_str)
            test_weight = self.get_weight(name_str2)

            if test_weight and weight != test_weight:
                weight = test_weight

            weight = int(weight) * int(count)

            pid = urlparse.parse_qs(url)['pid'][0]

            origin_str = Directory.normalize(origin_str)
            origin = self.get_origin(origin_str)

            price = int(price_str)
        except:
            log.error(Directory.ERROR_MAP[3] % (name_str, url))
            return None, None

        product = Product(source=GeantBrowser.INDEX_ROUTE,
                          name=name, origin=origin,
                          market_id=self.market.id,
                          pid=pid, weight=weight)

        price = Price(price=price, date=self.date)

        return product, price


class FengKangBrowser(MarketBrowser):

    NAME = '楓康'

    PRODUCTS_ROUTE = 'http://shop.supermarket.com.tw/Shop_ProductList.html?c0=%s&c1=%s&c2=%s&page=%s'
    INDEX_ROUTE = 'http://shop.supermarket.com.tw'

    PRODUCT_MAP = {
        '雞肉': [(1, 160, 330, 1), (1, 160, 330, 2)],
        '豬肉': [(1, 160, 331, 1), (1, 160, 330, 2)],
        '蔬菜': [(1, 159, 324, 1), (1, 159, 324, 2), (1, 159, 462, 1),
               (1, 159, 462, 2), (1, 159, 319, 1), (1, 159, 319, 2)],
        '水果': [(1, 365, 320, 1), (1, 365, 320, 2)],
        '雜貨': [(0, 153, 357, 1)],
    }

    NAME_RE = re.compile('''
        (?:.+?)(?=\d+.*|約.*|\W+.*|$)
    ''', re.X)

    PID_RE = re.compile('''
        p-(.+)(?=.html)
    ''', re.X)

    ORIGIN_RE = re.compile('''
        (?<=產　　地：)(.*)
    ''', re.X)

    COUNT_RE = re.compile('''
       \*(\d+)(?=[包粒顆盒]) 
    ''', re.X)

    def __init__(self):
        super(FengKangBrowser, self).__init__()

    @staticmethod
    def get_product_urls(map_str):
        url = FengKangBrowser.PRODUCTS_ROUTE % (map_str[0], map_str[1], map_str[2], map_str[3])
        page = MarketBrowser.get_html(url)
        urls = page.xpath('//div[@class="lisa3 lisa3-2"]//div[@class="t2"]/a/@href')
        return [FengKangBrowser.INDEX_ROUTE + url for url in set(urls)]

    def get_product_price(self, url):
        page = MarketBrowser.get_html(url)
        name_weight_str = ''.join(page.xpath('//div[@class="vw"]/div[@class="tt21"]/text()')).strip()
        price_str = ''.join(page.xpath('//div[@class="vw"]/div[@class="tt23"]//h4/text()')).strip()
        origin_str = ''.join(page.xpath('//div[@id="tab1"]/div[contains(string(), "產　　地：")]/text()')).strip()
        try:
            name = FengKangBrowser.NAME_RE.findall(name_weight_str)[0]

            weight = self.get_weight(name_weight_str)
            weight = int(weight)

            pid = FengKangBrowser.PID_RE.findall(url)[0]

            origin_str = Directory.normalize(origin_str)
            try:
                origin_str = FengKangBrowser.ORIGIN_RE.findall(origin_str)[0]
            except:
                origin_str = '其他'
            origin = self.get_origin(origin_str)

            price = int(price_str)

            try:
                count = FengKangBrowser.COUNT_RE.findall(name_weight_str)[0]
                count = int(count)
                weight = weight * count
            except IndexError:
                pass
        except:
            log.error(Directory.ERROR_MAP[3] % (name_weight_str, url))
            return None, None

        product = Product(source=FengKangBrowser.INDEX_ROUTE,
                          name=name, origin=origin,
                          market_id=self.market.id,
                          pid=pid, weight=weight)

        price = Price(price=price, date=self.date)

        return product, price


class RtmartBrowser(MarketBrowser):

    NAME = '大潤發'

    FRESH_ROUTE = 'http://www.rt-mart.com.tw/fresh/index.php?action=product_sort&prod_sort_uid=%s&p_data_num=200'
    NORMAL_ROUTE = 'http://www.rt-mart.com.tw/direct/index.php?action=product_sort&prod_sort_uid=%s&p_data_num=200'

    INDEX_ROUTE = 'http://www.rt-mart.com.tw'

    PRODUCT_MAP = {
        '雞肉': ['52697'], '豬肉': ['52696'],
        '蔬菜': ['52494'], '水果': ['52495'],
        '雜貨': ['3767']
    }

    NAME_RE = re.compile('''
        (?:.+?)(?=\d+.*|\(約+.*|$)
    ''', re.X)

    ORIGIN_RE = re.compile('''
        (?<=產地:)(?:.+?)(?=\\r\\n)
    ''', re.X)

    WEIGHT_RE = re.compile('''
        (?<=規格:)(?:.+?)(?=\\r\\n)
    ''', re.X)

    def __init__(self):
        super(RtmartBrowser, self).__init__()

    @staticmethod
    def get_product_urls(map_str):
        if len(map_str) == 4:
            url = RtmartBrowser.FRESH_ROUTE % map_str
        else:
            url = RtmartBrowser.NORMAL_ROUTE % map_str
        page = MarketBrowser.get_html(url)
        urls = page.xpath('//div[@class="classify_prolistBox"]//h5[@class="for_proname"]/a/@href')
        return [url for url in set(urls)]

    def get_product_price(self, url):
        page = MarketBrowser.get_html(url)
        name_str = ''.join(page.xpath('//div[@class="pro_rightbox"]/h2[@class="product_Titlename"]/span/text()')).strip()
        price_str = ''.join(page.xpath('//div[@class="product_PRICEBOX"]//span[@class="price_num"]/text()')).strip()
        intro_str = ''.join(page.xpath('//table[@class="title_word"]//table/tr/td/text()')).strip()
        try:
            name = RtmartBrowser.NAME_RE.findall(name_str)[0]

            intro_str = Directory.normalize(intro_str)

            try:
                weight_str = RtmartBrowser.WEIGHT_RE.findall(intro_str)[0]
            except IndexError:
                weight_str = name_str

            weight = self.get_weight(weight_str)
            test_weight = self.get_weight(name_str)

            if test_weight and weight != test_weight:
                weight = test_weight

            weight = int(weight)

            pid = urlparse.parse_qs(url)['prod_no'][0]

            try:
                origin_str = RtmartBrowser.ORIGIN_RE.findall(intro_str)[0]
            except IndexError:
                if u'台灣' in name:
                    origin_str = u'臺灣'
                else:
                    origin_str = '其他'
            origin = self.get_origin(origin_str)

            price_str = Directory.NUM_RE.findall(price_str)[0]
            price = int(price_str)

        except:
            log.error(Directory.ERROR_MAP[3] % (name_str, url))
            return None, None

        product = Product(source=RtmartBrowser.INDEX_ROUTE,
                          name=name, origin=origin,
                          market_id=self.market.id,
                          pid=pid, weight=weight)

        price = Price(price=price, date=self.date)

        return product, price







































