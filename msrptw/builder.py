#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
import sys
from argparse import ArgumentParser
from .database import config
from .marketbrowser import MarketBrowser, WellcomeBrowser, FengKangBrowser, GeantBrowser, RtmartBrowser


def build(db_path, setup):
    if db_path:
        config.setup_session(db_path)
        if setup:
            config.init()
        w = WellcomeBrowser()
        g = GeantBrowser()
        f = FengKangBrowser()
        r = RtmartBrowser()
        w.direct()
        g.direct()
        f.direct()
        r.direct()
        MarketBrowser.clear_stack()


def parse_args(args):
    parser = ArgumentParser()
    parser.add_argument('--dbpath', help='sql connection here.', required=True)
    parser.add_argument('--setup', help='present to initialize database.', action='store_true')
    return parser.parse_args()


def main(args):
    args = parse_args(args)
    build(args.dbpath, args.setup)


if __name__ == '__main__':
    main(sys.argv[1:])
