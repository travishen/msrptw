#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
import requests
import logging
import json
import sys
import datetime
from logging.config import fileConfig
from sqlalchemy.orm import subqueryload
from .database.config import session_scope
from . import _logging_config_path
from .database.model import Market, Product, Config, Price, Part
from .directory import Directory

fileConfig(_logging_config_path)
log = logging.getLogger(__name__)


class HonestBee(Directory):

    INDEX_ROUTE = 'https://www.honestbee.tw/zh-TW'
    API_ROUTE = 'https://www.honestbee.tw/api/api/departments/%s'

    STACK = []

    INFO_MAP = {
        0: '訪問HonestBee的%s取得所有%s商品',
    }

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
                amount_str = dic.get('amountPerUnit')

                pid = str(dic.get('id'))
                name = Directory.normalize(name_str)

                weight_str = Directory.normalize(size_str)
                weight = Directory.get_weight(weight_str)

                price = float(price_str)

                if unit_type == 'unit_type_item':
                    weight = weight * float(amount_str)

                origin = Directory.get_origin(name, default='臺灣')

            except:
                d = {
                    'title': name_str,
                    'unit_type': unit_type,
                    'size': size_str,
                    'amount_unit': amount_str,
                    'price': price_str
                }
                log.error(Directory.ERROR_MAP[5] % d)
                return dic

            price = Price(price=price,
                          weight=weight,
                          date=self.date)

            product = Product(source=HonestBee.INDEX_ROUTE,
                              name=name,
                              market_id=self.market.id,
                              pid=pid,
                              origin=origin)

            return product, price

        results = []

        page = map_str[2]

        for i in range(1, page+1):

            ps = self.api(config_id=map_str[0],
                          store_id=self.STORE_ID,
                          category_ids=map_str[1],
                          page=i,
                          header=self.header,
                          hook=hook)

            try:
                for item in ps:
                    if isinstance(item[0], Product) and isinstance(item[1], Price):
                        results.append(item)
            except KeyError:
                pass
        return results

    def direct(self):

        for config in self.configs:

            log.info(HonestBee.INFO_MAP[0] % (self.market.name, config.name))

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


class Rtmart(HonestBee):

    NAME = '大潤發'

    STORE_ID = 243

    PRODUCT_MAP = {
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
