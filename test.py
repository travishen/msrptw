#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import unicode_literals
import unittest
import os
from msrptw import marketbrowser
from msrptw.database import config


def get_success_rate(obj):
    success_rate = 0
    if isinstance(obj, marketbrowser.MarketBrowser):
        error_count = 0
        test_count = 0
        for key, value in obj.PRODUCT_MAP.items():
            urls = obj.get_product_urls(value[0])
            for url in urls[:3]:
                test_count += 1
                product, price = obj.get_product_price(url)
                if not product or not price:
                    error_count += 1
        success_rate = (test_count - error_count) / test_count
    return test_count, success_rate


class TestDB(unittest.TestCase):
    def setUp(self):
        db_path = os.getenv("DB_TEST_URL")
        if not db_path:
            self.skipTest("No database URL set")

        config.setup_session(db_path)
        with config.session_scope() as session:
            session.connection().connection.set_isolation_level(0)
            session.execute('CREATE DATABASE testdb')
            session.connection().connection.set_isolation_level(1)
        config.init()

    def tearDown(self):
        with config.session_scope() as session:
            session.connection().connection.set_isolation_level(0)
            session.execute('Drop DATABASE testdb')
            session.connection().connection.set_isolation_level(1)

    def test_wellcome(self):
        browser = marketbrowser.WellcomeBrowser()
        test_count, success_rate = get_success_rate(browser)
        print('%s: %.0f%% urls of %.0f successfully parsing' % (browser, test_count, success_rate * 100))
        self.assertTrue(success_rate > 0.7)
