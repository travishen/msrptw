#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
from sqlalchemy import Integer, Column, ForeignKey, Sequence, String, Unicode, Text
from sqlalchemy.orm import relationship, subqueryload
from json import JSONEncoder
from . import _base


class Config(_base):
    __tablename__ = 'config'
    id = Column(Integer, Sequence('config_id_seq'), primary_key=True, nullable=False)
    name = Column(Unicode(5))
    parts = relationship('Part')


class Part(_base):
    __tablename__ = 'part'
    id = Column(Integer, Sequence('part_id_seq'), primary_key=True, nullable=False)
    name = Column(Unicode(5))
    markets = relationship('Product', back_populates='part')


class Market(_base):
    __tablename__ = 'market'
    id = Column(Integer, Sequence('market_id_seq'), primary_key=True, nullable=False)
    name = Column(Unicode(5))
    parts = relationship('Product', back_populates='market')


class Product(_base):
    __tablename__ = 'product'
    id = Column(Integer, Sequence('product_id_seq'), primary_key=True, nullable=False)
    part_id = Column(Integer, ForeignKey('part.id'), primary_key=True)
    part = relationship('Part', back_populates='markets')
    market_id = Column(Integer, ForeignKey('market.id'), primary_key=True)
    market = relationship('Market', back_populates='parts')
    name = Column(Unicode(30))
    origin = Column(Unicode(5))
    pid = Column(String(20))
    retails = relationship('Retail')


class Retail(_base):
    __tablename__ = 'retail'
    id = Column(Integer, Sequence('retail_id_seq'), primary_key=True, nullable=False)
    product_id = Column(Integer, ForeignKey('product.id'), primary_key=True)
    price = Column(Integer)
    gram = Column(Integer)






