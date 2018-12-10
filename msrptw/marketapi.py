#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
import abc
import requests
import json
import logging
import re
from lxml import html
from logging.config import fileConfig
from pathos.pools import _ThreadPool
from pathos.multiprocessing import cpu_count
from . import _logging_config_path
from .database.model import Product, Price
from .directory import Directory

fileConfig(_logging_config_path)
log = logging.getLogger(__name__)


class MarketApi(Directory):
    """MarketApi class use products getter api from website,
    loads response json with Product and Price class and do
    further with Directory methods"""
    __meta__ = abc.ABCMeta

    @abc.abstractmethod
    def api(self):
        return

    @abc.abstractmethod
    def get_products_prices(self):
        return

    def direct(self):

        def browse_each(config):

            log.info(Directory.INFO_MAP[0] % (self.market.name, config.name))

            try:

                map_strs = self.PRODUCT_MAP[config.name]

                for map_str in map_strs:

                    results = self.get_products_prices(map_str)

                    for product, price in results:

                        product = Directory.check_product(product)

                        if not product.id:
                            Directory.STACK.append((config, product, price))

                        elif product.part_id:
                            price.product = product
                            Directory.set_price(price)

            except KeyError:
                log.error(Directory.ERROR_MAP[1] % config.name)

        cpu = cpu_count()
        pool = _ThreadPool(cpu)
        for c in self.configs:
            pool.apply_async(browse_each, args=(c, ))
        pool.close()
        pool.join()


class CarrfourBrowser(MarketApi):

    NAME = '家樂福'

    API_ROUTE = 'https://online.carrefour.com.tw/Catalog/CategoryJson'
    INDEX_ROUTE = 'https://online.carrefour.com.tw'

    # (category_id, size)
    PRODUCT_MAP = {
        '常溫商品': [('469', 20), ('2963', 10), ('2964', 10), ('2965', 10), ('468', 10),
                 ('433', 10), ('434', 10)],
        '冷藏商品': [('515', 20), ('366', 100), ('52', 35), ('17', 35)],
        '海鮮': [('2972', 35), ('145', 35), ('172', 35)],
        '牛肉': [('194', 35)], '羊肉': [('199', 35)],
        '雞肉': [('206', 35)], '豬肉': [('201', 35)],
        '蔬菜': [('215', 15), ('216', 15), ('217', 15), ('218', 15), ('219', 15), ('220', 15),
               ('224', 35), ('223', 15), ('222', 15), ('221', 15)],
        '水果': [('231', 70)],
        '雜貨': [('471', 100), ('522', 20), ('527', 20)]
    }

    NAME_RE = re.compile('''
        (?:.+?)(?=[\d-]+.*|$)
    ''', re.X)

    @staticmethod
    def api(category_id, size, hook=None):
        params = {
            'categoryId': category_id,
            'orderBy': 21,
            'pageIndex': 1,
            'pageSize': size
        }
        res = requests.post(CarrfourBrowser.API_ROUTE, params=params)
        dic = json.loads(res.text, object_hook=hook)
        return dic['content']['ProductListModel']

    def get_products_prices(self, map_str):

        def hook(dic):

            if not dic.get('Price'):
                return dic

            try:
                name_str = dic.get('Name')
                price_str = dic.get('Price')
                special_price = dic.get('SpecialPrice')
                count_str = dic.get('ItemQtyPerPack')
                origin_route = dic.get('SeName')
                pid = str(dic.get('Id'))

                # 紅蘿蔔500g => 紅蘿蔔
                name = self.NAME_RE.findall(name_str)[0]

                # get special price rather than normal price
                if special_price:
                    price = float(special_price)
                else:
                    price = float(price_str)

                # get origin_str and weight_str from page
                product_url = self.INDEX_ROUTE + origin_route
                origin_str, weight_str, unit_str = self.get_infos(product_url)
                origin = Directory.get_origin(origin_str, default='其他')

                if weight_str:
                    weight = self.get_weight(weight_str)
                # try to find weight in title
                else:
                    weight = self.get_weight(name_str)

                unit = self.get_unit(unit_str)

                count = int(count_str)

            except:
                d = {
                    'Name': name_str,
                    'ItemQtyPerPack': count_str,
                    'Price': price_str
                }
                log.error(Directory.ERROR_MAP[5] % d)
                return dic

            price = Price(price=price,
                          date=self.date)

            product = Product(source=product_url,
                              name=name,
                              market_id=self.market.id,
                              pid=pid,
                              origin=origin,
                              weight=weight,
                              count=count,
                              unit=unit)

            return product, price

        results = []

        ps = self.api(category_id=map_str[0],
                      size=map_str[1],
                      hook=hook)

        for item in ps:
            try:
                if isinstance(item[0], Product) and isinstance(item[1], Price):
                    results.append(item)
            except KeyError:
                pass

        return results

    @staticmethod
    def get_infos(url):

        res = requests.get(url)
        page = html.fromstring(res.content)

        xpath = Directory.flat_xpath

        origin_str = xpath(page, '''
            //div[@id="pro-content2"]//div[contains(string(), "商品來源")]/following-sibling::div[1]/text()
        ''')

        weight_str = xpath(page, '''
            //div[@id="pro-content2"]//div[contains(string(), "重量")]/following-sibling::div[1]/text()
        ''')

        unit_str = xpath(page, '''
            //div[@id="pro-content2"]//div[contains(string(), "容量")]/following-sibling::div[1]/text()
        ''')

        return origin_str, weight_str, unit_str


class HonestBee(MarketApi):

    INDEX_ROUTE = 'https://www.honestbee.tw/zh-TW'
    API_ROUTE = 'https://www.honestbee.tw/api/api/departments/%s'

    def __init__(self, **args):
        super(HonestBee, self).__init__()
        if not self.STORE_ID:
            raise NotImplementedError
        lan = args.get('lan', 'zh-TW')
        self.header = {
            'Accept': 'application/vnd.honestbee+json;version=2',
            'Accept-Language': lan
        }

    @staticmethod
    def api(config_id, store_id, category_ids, page, header, hook=None):

        params = {
            'categoryIds[]': category_ids,
            'sort': 'ranking',
            'storeId': store_id,
            'page': page
        }

        res = requests.get(HonestBee.API_ROUTE % config_id, params=params, headers=header)
        dic = json.loads(res.text, object_hook=hook)
        return dic['products']

    def get_products_prices(self, map_str):

        def hook(dic):

            if dic.get('status') != 'status_available':
                return dic

            try:
                name_str = dic.get('title')
                unit_type = dic.get('unitType')
                price_str = dic.get('price')
                size_str = dic.get('size')

                pid_str = dic.get('pid')

                pid = str(pid_str)
                name = self.normalize(name_str)
                weight_str = self.normalize(size_str)
                price = float(price_str)

                # try to find unit in size key
                count = self.get_count(size_str)

                # try to find weight in size key
                weight = self.get_weight(weight_str)

                # try to find origin in title key
                origin = self.get_origin(name_str, default='臺灣')

                # try to find unit in title
                unit = self.get_unit(name_str)

            except:
                d = {
                    'title': name_str,
                    'unit_type': unit_type,
                    'size': size_str,
                    'price': price_str
                }
                log.error(Directory.ERROR_MAP[5] % d)
                return dic

            price = Price(price=price,
                          date=self.date)

            product = Product(source=HonestBee.INDEX_ROUTE,
                              name=name,
                              market_id=self.market.id,
                              pid=pid,
                              origin=origin,
                              weight=weight,
                              count=count,
                              unit=unit)

            return product, price

        results = []

        page = map_str[2]

        for i in range(1, page + 1):

            ps = self.api(config_id=map_str[0],
                          store_id=self.STORE_ID,
                          category_ids=map_str[1],
                          page=i,
                          header=self.header,
                          hook=hook)

            for item in ps:
                try:
                    if isinstance(item[0], Product) and isinstance(item[1], Price):
                        results.append(item)
                except KeyError:
                    pass

        return results


class Rtmart(HonestBee):
    NAME = '大潤發'

    STORE_ID = 243

    PRODUCT_MAP = {
        '常溫商品': [(9280, ['48425'], 3), (9280, ['48424'], 1),
                 (9277, ['48399'], 1), (9277, ['48395'], 1),
                 (9279, ['48420'], 1), (9279, ['48419'], 1),
                 (9280, ['48426'], 1)],
        '冷藏商品': [(6982, ['35779'], 2), (6982, ['35773'], 1), (6982, ['35776'], 1), (6982, ['35774'], 1)],
        '海鮮': [(6989, ['35811'], 1), (6989, ['85719'], 1), (6989, ['35810'], 1)],
        '牛肉': [(6990, ['35812'], 1)],

        '雞肉': [(6990, ['35814'], 2)],
        '豬肉': [(6990, ['35813'], 2)],
        '蔬菜': [(6980, ['37013'], 1), (6980, ['37014'], 1),
               (6980, ['35762'], 2), (6980, ['72745'], 1),
               (6980, ['37016'], 1), (6980, ['72744'], 1),
               (6980, ['35759'], 1), (6980, ['35763'], 1),
               (6980, ['35760'], 1), (6980, ['37012'], 1),
               (6980, ['35761'], 1)],
        '雜貨': [(6981, ['35769'], 3)],
        '水果': [(6988, ['37019'], 1), (6988, ['37018'], 1),
               (6988, ['35809'], 1), (6988, ['37017'], 1),
               (6988, ['37020'], 1), (6988, ['37021'], 1)]
    }


class Carrefour(HonestBee):
    NAME = '家樂福'

    STORE_ID = 74

    PRODUCT_MAP = {
        '常溫商品': [(7203, ['37472'], 2), (7203, ['37473'], 2)],
        '冷藏商品': [(7204, ['37478'], 2), (7204, ['37479'], 1), (7204, ['37481'], 1),
                 (7204, ['37484'], 1), (7204, ['37483'], 1)],
        '海鮮': [(7214, ['37351'], 1), (7214, ['37532'], 1)],
        '牛肉': [(7211, ['37520'], 1)],

        '雞肉': [(7211, ['37522'], 1)],
        '豬肉': [(7211, ['37521'], 1)],
        '水果': [(7213, ['37530'], 1)],
        '蔬菜': [(7215, ['37537'], 1), (7215, ['37539'], 1),
               (7215, ['37536'], 1), (7215, ['37538'], 1),
               (7215, ['37540'], 1), (7215, ['37533'], 1),
               (7215, ['37534'], 1), (7215, ['37535'], 1),
               (7215, ['71957'], 1)]
    }


class BinJung(HonestBee):
    NAME = '濱江'

    STORE_ID = 435

    PRODUCT_MAP = {
        '雞肉': [(6559, ['33371'], 1)],
        '豬肉': [(6559, ['33370'], 1)],
        '蔬菜': [(6556, ['33352'], 1), (6556, ['33350'], 2),
               (6556, ['33355'], 1), (6556, ['33348'], 1),
               (6556, ['33347'], 1), (6556, ['33357'], 1),
               (6556, ['33354'], 1), (6556, ['33351'], 1),
               (6556, ['33353'], 1), (6556, ['33356'], 1),
               (6556, ['33346'], 1)],
        '水果': [(6557, ['33365'], 1), (6557, ['33363'], 1),
               (6557, ['33362'], 1)]
    }


class NewTaipeiCenter(HonestBee):
    NAME = '新北市農產中心'

    STORE_ID = 2152

    PRODUCT_MAP = {
        '雞肉': [(9554, ['49710'], 1)],
        '豬肉': [(9554, ['49709'], 1)],
        '蔬菜': [(9548, ['49673'], 1), (9548, ['49668'], 1),
               (9548, ['49671'], 1), (9548, ['49674'], 1),
               (9548, ['49667'], 1), (9548, ['49677'], 1),
               (9548, ['49675'], 1), (9548, ['49669'], 1),
               (9548, ['49672'], 1), (9548, ['49670'], 1),
               (9548, ['49676'], 1)],
        '水果': [(9552, ['49703'], 1), (9552, ['49699'], 1),
               (9552, ['49700'], 1)]
    }
