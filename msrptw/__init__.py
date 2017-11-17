#!/usr/bin/env python

from os.path import dirname, join
from . import handler

#paths
_package_root = dirname(__file__)
_logging_config_path = join(_package_root, 'logging.ini')

SQLAlchemyHandler = handler.SQLAlchemyHandler

