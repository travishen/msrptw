#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
import logging
from .database.config import session_scope
from .database.model import Log


class SQLAlchemyHandler(logging.Handler):
    def emit(self, record):
        log = Log(
            logger=record.__dict__['name'],
            level=record.__dict__['levelname'],
            msg=record.__dict__['msg'], )
        with session_scope() as session:
            session.add(log)