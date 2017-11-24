#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
from sqlalchemy import Integer, Column, ForeignKey, Sequence, String, Unicode, Date, DateTime, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from . import _base


class Config(_base):
    __tablename__ = 'config'
    id = Column(Integer, Sequence('config_id_seq'), primary_key=True, nullable=False)
    name = Column(Unicode(5))
    parts = relationship('Part')


class Part(_base):
    __tablename__ = 'part'
    id = Column(Integer, Sequence('part_id_seq'), primary_key=True, nullable=False)
    config_id = Column(Integer, ForeignKey('config.id'))
    config = relationship('Config', back_populates='parts')
    products = relationship('Product')
    name = Column(Unicode(15))
    aliases = relationship('Alias')



class Alias(_base):
    __tablename__ = 'alias'
    id = Column(Integer, Sequence('alias_id_seq'), primary_key=True, nullable=False)
    part_id = Column(Integer, ForeignKey('part.id'))
    part = relationship('Part', back_populates='aliases')
    name = Column(Unicode(15))
    anti = Column(Boolean, default=False)
    products = relationship('Product')


class Market(_base):
    __tablename__ = 'market'
    id = Column(Integer, Sequence('market_id_seq'), primary_key=True, nullable=False)
    name = Column(Unicode(10))
    products = relationship('Product')


class Origin(_base):
    __tablename__ = 'origin'
    id = Column(Integer, Sequence('origin_id_seq'), primary_key=True, nullable=False)
    name = Column(Unicode(5))
    products = relationship('Product')


class Product(_base):
    __tablename__ = 'product'
    id = Column(Integer, Sequence('product_id_seq'), primary_key=True, nullable=False)
    part_id = Column(Integer, ForeignKey('part.id'))
    part = relationship('Part', back_populates='products')
    market_id = Column(Integer, ForeignKey('market.id'))
    market = relationship('Market', back_populates='products')
    origin_id = Column(Integer, ForeignKey('origin.id'))
    origin = relationship('Origin', back_populates='products')
    alias_id = Column(Integer, ForeignKey('alias.id'))
    alias = relationship('Alias', back_populates='products')
    name = Column(Unicode(30))
    pid = Column(String(20))
    source = Column(String(255))
    weight = Column(Integer)
    prices = relationship('Price')


class Price(_base):
    __tablename__ = 'price'
    id = Column(Integer, Sequence('price_id_seq'), primary_key=True, nullable=False)
    product_id = Column(Integer, ForeignKey('product.id'))
    product = relationship('Product', back_populates='prices')
    price = Column(Integer)
    date = Column(Date)


class Log(_base):
    __tablename__ = 'log'
    id = Column(Integer, Sequence('log_id_seq'), primary_key=True, nullable=False)
    logger = Column(String)
    level = Column(String)
    msg = Column(String)
    datetime = Column(DateTime, default=func.now())

    def __init__(self, logger=None, level=None, trace=None, msg=None):
        self.logger = logger
        self.level = level
        self.trace = trace
        self.msg = msg

    def __unicode__(self):
        return self.__repr__()

    def __repr__(self):

        return '<Log: %s - %s>' % (self.created_at.strftime('%m/%d/%Y-%H:%M:%S'), self.msg[:50])





