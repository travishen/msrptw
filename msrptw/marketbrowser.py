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
from multiprocessing import Pool, cpu_count
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
        0: '商品重量單位轉換失敗',
        1: '找不到相對應的品項媒合值',
        2: '定義商品部位輸入無效的字串',
        3: '處理文本%s發生溢位或值錯誤\n請查看原始頁面:(%s)',
        4: '訪問商品頁面(%s)請求逾時'
    }

    INFO_MAP = {
        0: '訪問%s取得所有%s商品',
        1: '無法自動分類商品「%s」，產地%s，請定義產品類型或放棄(Enter)\n%s:',
        2: '將商品%s人工定義為%s',
        3: '放棄定義商品%s',
        4: '將商品%s自動定義為%s'
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
        'KG': (0, 1000), 'G': (1, 1), 'g': (1, 1), 'kg': (0, 1000), 'Kg': (0, 1000),
        '公斤': (0, 1000), '公克': (1, 1), '克': (1, 1)
    }

    UNIT_RE = re.compile('''
        (?:
            (?P<kg>\d+?.\d+|\d+)(?=KG|kg|Kg|公斤)
            |
            (?P<g>\d+?.\d+|\d+)(?=G|g|公克|克)
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
        def browse_each(config, urls):
            for url in urls:
                product, price = self.get_product_price(url)
                if not product and not price:
                    continue
                # return self if not exists
                product = self.check_product(product)
                if not product.id:
                    MarketBrowser.STACK.append((config, product, price))
                else:
                    price.product = product
                    self.set_price(price)

        cpu = cpu_count()
        pool = Pool(processes=cpu)
        results = []
        for c, u in self.config_generator(product_map):
            process = pool.apply_async(browse_each(c, u))
            results.append(process)
        for process in results:
            process.wait()
        pool.close()
        pool.join()

    @classmethod
    def clear_stack(cls):
        def set_product_price(pd, pc):
            pc.product = pd
            MarketBrowser.set_price(pc)

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
                if alias.name in product.name and not alias.anti:
                    find = True
            for alias in part.aliases:
                if alias.name in product.name and alias.anti:
                    find = False
            if find:
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
                break
            else:
                try:
                    i = int(i)
                except ValueError:
                    log.error(MarketBrowser.ERROR_MAP[2])
                    continue
                if i in range(config.parts.__len__()):
                    product.part_id = config.parts[i].id
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

    @staticmethod
    def get_html(url):
        try:
            res = requests.get(url, timeout=15)
            parsed_page = html.fromstring(res.content)
        except requests.exceptions.Timeout:
            log.error(MarketBrowser.ERROR_MAP[4] % url)
            return html.Element('html')
        return parsed_page

    def __init__(self, market_name):
        self.date = datetime.date.today().strftime('%Y-%m-%d')
        with session_scope() as session:
            self.configs = session.query(Config).options(subqueryload(Config.parts).subqueryload(Part.aliases)).all()
            self.market = session.query(Market).filter(Market.name == market_name).first()
            session.expunge_all()


class WellcomeBrowser(MarketBrowser):

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
        super(WellcomeBrowser, self).__init__(WellcomeBrowser.NAME)

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
            weight_token = MarketBrowser.UNIT_RE.findall(weight_str)
            weight = self.get_weight(weight_token[0])
            pid = MarketBrowser.NUM_RE.findall(url)[-1]
            origin = self.get_origin(origin_str)
            weight = int(weight)
            price = int(price_str)
        except:
            log.error(MarketBrowser.ERROR_MAP[3] % (name_str, url))
            return None, None

        product = Product(name=name, origin=origin, market_id=self.market.id, pid=pid)
        price = Price(price=price, weight=weight, date=self.date)
        return product, price


class GeantBrowser(MarketBrowser):

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
        super(GeantBrowser, self).__init__(GeantBrowser.NAME)

    @staticmethod
    def get_product_urls(map_str):
        url = GeantBrowser.PRODUCTS_ROUTE % (map_str)
        page = MarketBrowser.get_html(url)
        urls = page.xpath('//ul[@class="product_list"]//h5/a/@href')
        return [GeantBrowser.INDEX_ROUTE + url for url in set(urls)]

    def get_product_price(self, url):
        def replace(s):
            return re.sub(r'台', '臺', s)
        page = MarketBrowser.get_html(url)
        name_str = ''.join(page.xpath('''
            //div[@class="product_content"]//tr[contains(string(), "商品")]/td[2]//text()
        ''')).strip()
        intro_str = ''.join(page.xpath('//dd[@class="introduction"]/text()')).strip()
        price_str = ''.join(page.xpath('//dd[@class="list_price"]/text()')).strip()
        try:
            name = ''.join([s for s in name_str if s.isalnum()])
            if not name:
                name = ''.join(page.xpath('//h3[@class="trade_Name"]/text()')).strip()
            name = GeantBrowser.NAME_RE.findall(name)[0]

            try:
                origin_str = GeantBrowser.ORIGIN_RE.findall(intro_str)[0]
            except IndexError:
                origin_str = ''.join(page.xpath('''
                    //div[@class="product_content"]//tr[contains(string(), "產地")]/td[2]//text()
                ''')).strip()

            count_str = GeantBrowser.COUNT_RE.findall(intro_str)[0]
            count = MarketBrowser.NUM_RE.findall(count_str)[0]

            weight_str = GeantBrowser.WEIGHT_RE.findall(intro_str)[0]
            weight_token = MarketBrowser.UNIT_RE.findall(weight_str)
            weight = self.get_weight(weight_token[0])
            weight = int(weight) * int(count)

            pid = urlparse.parse_qs(url)['pid'][0]

            origin_str = replace(origin_str)
            origin = self.get_origin(origin_str)

            price = int(price_str)
        except:
            log.error(MarketBrowser.ERROR_MAP[3] % (name_str, url))
            return None, None

        product = Product(name=name, origin=origin, market_id=self.market.id, pid=pid)
        price = Price(price=price, weight=weight, date=self.date)
        return product, price


class FengKangBrowser(MarketBrowser):

    NAME = '楓康'

    PRODUCTS_ROUTE = 'http://shop.supermarket.com.tw/Shop_ProductList.html?c0=%s&c1=%s&c2=%s&page=%s'
    INDEX_ROUTE = 'http://shop.supermarket.com.tw'

    PRODUCT_MAP = {
        '雞肉': [(1, 160, 330, 1), (1, 160, 330, 2)],
        '豬肉': [(1, 160, 331, 1), (1, 160, 330, 2)],
        '蔬菜': [(1, 159, 324, 1), (1, 159, 324, 2), (1, 159, 462, 1), (1, 159, 462, 2), (1, 159, 319, 1), (1, 159, 319, 2)],
        '水果': [(1, 365, 320, 1), (1, 365, 320, 2)],
        '雜貨': [(0, 153, 357, 1), (0, 153, 357, 2)],
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
        super(FengKangBrowser, self).__init__(FengKangBrowser.NAME)

    @staticmethod
    def get_product_urls(map_str):
        url = FengKangBrowser.PRODUCTS_ROUTE % (map_str[0], map_str[1], map_str[2], map_str[3])
        page = MarketBrowser.get_html(url)
        urls = page.xpath('//div[@class="lisa3 lisa3-2"]//div[@class="t2"]/a/@href')
        return [FengKangBrowser.INDEX_ROUTE + url for url in set(urls)]

    def get_product_price(self, url):
        def replace(s):
            return re.sub(r'台', '臺', s)
        page = MarketBrowser.get_html(url)
        name_weight_str = ''.join(page.xpath('//div[@class="vw"]/div[@class="tt21"]/text()')).strip()
        price_str = ''.join(page.xpath('//div[@class="vw"]/div[@class="tt23"]//h4/text()')).strip()
        origin_str = ''.join(page.xpath('//div[@id="tab1"]/div[contains(string(), "產　　地：")]/text()')).strip()
        try:
            name = FengKangBrowser.NAME_RE.findall(name_weight_str)[0]

            weight_token = MarketBrowser.UNIT_RE.findall(name_weight_str)
            weight = self.get_weight(weight_token[0])
            weight = int(weight)

            pid = FengKangBrowser.PID_RE.findall(url)[0]

            origin_str = replace(origin_str)
            origin_str = FengKangBrowser.ORIGIN_RE.findall(origin_str)[0]
            origin = self.get_origin(origin_str)

            price = int(price_str)

            try:
                count = FengKangBrowser.COUNT_RE.findall(name_weight_str)[0]
                count = int(count)
                weight = weight * count
            except IndexError:
                pass
        except:
            log.error(MarketBrowser.ERROR_MAP[3] % (name_weight_str, url))
            return None, None

        product = Product(name=name, origin=origin, market_id=self.market.id, pid=pid)
        price = Price(price=price, weight=weight, date=self.date)
        return product, price


class RtmartBrowser(MarketBrowser):

    NAME = '大潤發'

    PRODUCTS_ROUTE = 'http://www.rt-mart.com.tw/fresh/index.php?action=product_sort&prod_sort_uid=%s&p_data_num=200'
    INDEX_ROUTE = 'http://www.rt-mart.com.tw'

    PRODUCT_MAP = {
        '雞肉': ['52697'], '豬肉': ['52696'],
        '蔬菜': ['52494'], '水果': ['52495'],
        '雜貨': ['54056']
    }

    NAME_RE = re.compile('''
        (?:.+?)(?=\d+.*|$)
    ''', re.X)

    ORIGIN_RE = re.compile('''
        (?<=產地:)(?:.+?)(?=\\r\\n)
    ''', re.X)

    WEIGHT_RE = re.compile('''
        (?<=規格:)(?:.+?)(?=\\r\\n)
    ''', re.X)

    def __init__(self):
        super(RtmartBrowser, self).__init__(RtmartBrowser.NAME)

    @staticmethod
    def get_product_urls(map_str):
        url = RtmartBrowser.PRODUCTS_ROUTE % (map_str)
        page = MarketBrowser.get_html(url)
        urls = page.xpath('//div[@class="classify_prolistBox"]//h5[@class="for_proname"]/a/@href')
        return [url for url in set(urls)]

    def get_product_price(self, url):
        def replace(s):
            return re.sub(r'台', '臺', s)
        page = MarketBrowser.get_html(url)
        name_str = ''.join(page.xpath('//div[@class="pro_rightbox"]/h2[@class="product_Titlename"]/span/text()')).strip()
        price_str = ''.join(page.xpath('//div[@class="product_PRICEBOX"]//span[@class="price_num"]/text()')).strip()
        intro_str = ''.join(page.xpath('//table[@class="title_word"]//table/tr/td/text()')).strip()
        try:
            name = RtmartBrowser.NAME_RE.findall(name_str)[0]

            intro_str = replace(intro_str)

            try:
                weight_str = RtmartBrowser.WEIGHT_RE.findall(intro_str)[0]
            except IndexError:
                weight_str = name_str
            weight_token = MarketBrowser.UNIT_RE.findall(weight_str)
            weight = self.get_weight(weight_token[0])
            weight = int(weight)

            pid = urlparse.parse_qs(url)['prod_no'][0]

            origin_str = None
            try:
                origin_str = RtmartBrowser.ORIGIN_RE.findall(intro_str)[0]
            except IndexError:
                if u'台灣' in name:
                    origin_str = u'臺灣'
            origin = self.get_origin(origin_str)

            price_str = MarketBrowser.NUM_RE.findall(price_str)[0]
            price = int(price_str)

        except:
            log.error(MarketBrowser.ERROR_MAP[3] % (name_str, url))
            return None, None

        product = Product(name=name, origin=origin, market_id=self.market.id, pid=pid)
        price = Price(price=price, weight=weight, date=self.date)
        return product, price



















