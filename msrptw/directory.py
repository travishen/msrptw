#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import datetime
import re
import logging
from sqlalchemy.orm import subqueryload
from logging.config import fileConfig
from . import _logging_config_path
from .database.config import session_scope
from .database.model import Market, Product, Config, Origin, Price, Part

fileConfig(_logging_config_path)
log = logging.getLogger(__name__)


class Directory(object):
    """initialize with class attribute NAME and loads instance
    attribute from sqlalchemy, as a database entry also provides
    basic text parsing settings"""

    NUM_RE = re.compile('''
            (?:\d+)
    ''', re.X)

    GLOBAL_REPLACE_RE = re.compile('''
        [ 　台]
        |
        [０-９]    
    ''', re.X)

    TO_REPLACE_MAP = {
        '台': '臺',
        '１': '1', '２': '2', '３': '3', '４': '4', '５': '5',
        '６': '6', '７': '7', '８': '8', '９': '9', '０': '0'
    }

    ORIGIN_MAP = {
        '臺北': '臺灣', '臺中': '臺灣', '基隆': '臺灣', '臺南': '臺灣', '高雄': '臺灣', '新北': '臺灣',
        '桃園': '臺灣', '嘉義': '臺灣', '新竹': '臺灣', '苗栗': '臺灣', '南投': '臺灣', '彰化': '臺灣',
        '屏東': '臺灣', '花蓮': '臺灣', '臺東': '臺灣', '金門': '臺灣', '澎湖': '臺灣', '臺灣': '臺灣',
        '西螺': '臺灣', '美濃': '臺灣', '雲林': '臺灣', '宜蘭': '臺灣', '履歷': '臺灣', '有機': '臺灣',
        '澳洲': '澳洲',
        '中國': '中國',
        '美國': '美國',
        '日本': '日本', '富士': '日本',
        '韓國': '韓國',
        '進口': '其他', '越南': '其他', '紐西': '其他', '南非': '其他', '智利': '其他', '泰國': '其他'
    }

    UNIT_MAP = {
        'kg': (0, 1000), 'l': (0, 1000),
        'g': (1, 1), 'ml': (1, 1), 'cc': (1, 1),
        '公斤': (0, 1000), '公克': (1, 1), '克': (1, 1),
        '公升': (0, 1000), '毫升': (1, 1),
    }

    UNIT_RE = re.compile('''
        (?:
            (?=\D?)
            (?P<kg>[0-9]+?\.[0-9]+|[0-9]+)(?=kg|公斤|公升|l)
            |
            (?=\D?)
            (?P<g>[0-9]+?\.[0-9]+|[0-9]+)(?=g|公克|克|毫升|ml|cc)
        )
    ''', re.X)

    MULTI_RE = re.compile('''
        (?:[*×xX][0-9]+)|(?:[0-9]+[*×xX])
    ''', re.X)

    STACK = []

    ERROR_MAP = {
        0: '商品重量單位轉換失敗',
        1: '找不到相對應的%s品項媒合值',
        2: '定義商品部位輸入無效的字串',
        3: '處理html文本%s發生溢位或值錯誤\n請查看原始頁面:(%s)',
        4: '訪問商品頁面(%s)請求逾時',
        5: '處理json文本發生溢位或值錯誤\n%s',
    }

    INFO_MAP = {
        0: '訪問%s取得所有%s商品',
        1: '無法自動分類商品「%s」，產地%s，請定義產品類型或放棄(Enter)\n%s:',
        2: '將商品%s人工定義為%s',
        3: '放棄定義商品%s',
        4: '將商品%s自動定義為%s'
    }

    def __init__(self):

        if not self.PRODUCT_MAP or not self.NAME:
            raise NotImplementedError

        self.date = datetime.date.today().strftime('%Y-%m-%d')

        with session_scope() as session:
            self.configs = session.query(Config).options(
                subqueryload(Config.parts).subqueryload(Part.aliases)
            ).all()
            self.market = session.query(Market).filter(Market.name == self.NAME).first()
            session.expunge_all()

    @staticmethod
    def normalize(s):

        def replace(m):

            found = m.group()

            if found in Directory.TO_REPLACE_MAP:
                return Directory.TO_REPLACE_MAP[found]

            return ''

        s = Directory.GLOBAL_REPLACE_RE.sub(replace, s)

        return s

    @staticmethod
    def get_origin(origin_str, default='其他'):

        origin_str = Directory.normalize(origin_str)

        def find(s):
            for key in Directory.ORIGIN_MAP.keys():
                if key in s:
                    return Directory.ORIGIN_MAP[key]
            return ''

        with session_scope() as session:
            value = find(origin_str)
            if value:
                origin = session.query(Origin).filter(Origin.name == value).first()
            else:
                origin = session.query(Origin).filter(Origin.name == default).first()
            session.expunge(origin)

        return origin

    @classmethod
    def clear_stack(cls):

        def set_product_price(pd, pc):

            if pd.part_id:
                pc.product = pd
                Directory.set_price(pc)
            else:
                Directory.set_product(pd)

        manuals = []

        for config, product, price in cls.STACK:
            product = Directory.classify_product_auto(config, product)
            if product.part_id:
                set_product_price(product, price)
            else:
                manuals.append((config, product, price))

        for config, product, price in manuals:
            product = Directory.classify_product_manual(config, product)
            set_product_price(product, price)

        cls.STACK = []

    @staticmethod
    def set_product(product):
        with session_scope() as session:
            session.add(product)

    @classmethod
    def get_weight(cls, weight_str):

        weight_str = cls.normalize(weight_str)

        # 120g*3入 => *3
        counts = cls.MULTI_RE.findall(weight_str)

        count = 1

        if counts:
            # 120*3g => 120g
            weight_str = re.sub(cls.MULTI_RE, '', weight_str)
            # *3 => 3
            count_str = ''.join([s for s in counts[0] if s.isalnum()])
            count = int(count_str)

        try:
            weight_str = weight_str.lower()
            token = cls.UNIT_RE.findall(weight_str)[0]
            for index, multiplier in cls.UNIT_MAP.values():
                unit_value = token[index]
                if unit_value:
                    try:
                        unit_value = float(unit_value)
                    except ValueError:
                        log.error(Directory.ERROR_MAP[0])
                        return None
                    # 120g*3 => 120 * 1 * 3
                    return unit_value * multiplier * count
        except:
            return None

    @staticmethod
    def classify_product_auto(config, product):
        for part in config.parts:
            find = False
            if part.name in product.name:
                find = True
            for alias in part.aliases:
                if alias.name in product.name and not alias.anti:
                    product.alias_id = alias.id
                    find = True
            for alias in part.aliases:
                if alias.name in product.name and alias.anti:
                    find = False
            if find:
                product.part_id = part.id
                log.info(Directory.INFO_MAP[4] % (product.name, part.name))
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
            i = input(Directory.INFO_MAP[1] % (product.name, product.origin.name, options))

            if not i:
                log.info(Directory.INFO_MAP[3] % product.name)
                break
            else:
                try:
                    i = int(i)
                except ValueError:
                    log.error(Directory.ERROR_MAP[2])
                    continue
                if i in range(config.parts.__len__()):
                    product.part_id = config.parts[i].id
                    log.info(Directory.INFO_MAP[2] % (product.name, config.parts[i].name))
                    break
        return product

    @staticmethod
    def check_product(product):
        with session_scope() as session:

            db_product = session.query(Product).filter(
                Product.pid == product.pid
            ).filter(
                Product.market_id == product.market_id
            ).first()

            if db_product:
                session.expunge(db_product)
                return db_product
            return product

    @staticmethod
    def set_price(price):
        with session_scope() as session:

            db_price = session.query(Price).filter(
                Price.date == price.date
            ).filter(
                Price.product_id == price.product.id
            ).first()

            if db_price:
                db_price.price = price.price
            else:
                session.add(price)