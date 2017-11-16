#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
import sys
from argparse import ArgumentParser
from .database import config


def build(db_path):
    if db_path:
        config.init(db_path)


def parse_args(args):
    parser = ArgumentParser()
    parser.add_argument('--dbpath', help='sql connection here.', required=True)
    return parser.parse_args()


def main(args):
    args = parse_args(args)
    build(args.dbpath)


if __name__ == '__main__':
    main(sys.argv[1:])
