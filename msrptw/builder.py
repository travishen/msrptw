#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
import sys
from argparse import ArgumentParser
from .database import config
from .directory import Directory
from . import marketbrowser, marketapi


def build(db_path, setup):
    if db_path:
        config.setup_session(db_path)
        if setup:
            config.init()

        w = marketbrowser.WellcomeBrowser()
        w.direct()

        f = marketbrowser.FengKangBrowser()
        f.direct()

        r1 = marketbrowser.RtmartBrowser()
        r1.direct()

        r2 = marketapi.Rtmart()
        r2.direct()

        c1 = marketapi.Carrefour()
        c1.direct()

        c2 = marketapi.CarrfourBrowser()
        c2.direct()

        b = marketapi.BinJung()
        b.direct()

        n = marketapi.NewTaipeiCenter()
        n.direct()

        Directory.clear_stack()


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
