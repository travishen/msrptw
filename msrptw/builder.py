#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
import sys
from argparse import ArgumentParser
from .database import config
from .directory import Directory
from . import marketbrowser, honestbee


def build(db_path, setup):
    if db_path:
        config.setup_session(db_path)
        if setup:
            config.init()

        w = marketbrowser.WellcomeBrowser()
        g = marketbrowser.GeantBrowser()
        f = marketbrowser.FengKangBrowser()
        r = marketbrowser.RtmartBrowser()
        w.direct()
        g.direct()
        f.direct()
        r.direct()

        r = honestbee.Rtmart()
        c = honestbee.Carrefour()
        b = honestbee.BinJung()
        n = honestbee.NewTaipeiCenter()
        r.direct()
        c.direct()
        b.direct()
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
