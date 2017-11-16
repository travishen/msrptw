#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
from sqlalchemy import Integer, Column, ForeignKey, Sequence, String, Unicode, Table
from sqlalchemy.orm import relationship
from json import JSONEncoder
from . import _base


class Config(_base):
    __tablename__ = 'config'
    id = Column(Integer, Sequence('config_id_seq'), primary_key=True, nullable=False)
    name = Column(Unicode(5))
    parts = relationship('Part')

    def parts_to_dict(self):
        return {'(%s) : %s  ' % (i, part.name) for i, part in enumerate(self.parts)}


class Part(_base):
    __tablename__ = 'part'
    id = Column(Integer, Sequence('part_id_seq'), primary_key=True, nullable=False)
    config_id = Column(Integer, ForeignKey('config.id'))
    config = relationship('Config', back_populates='parts')
    products = relationship('Product')
    name = Column(Unicode(5))


class Market(_base):
    __tablename__ = 'market'
    id = Column(Integer, Sequence('market_id_seq'), primary_key=True, nullable=False)
    name = Column(Unicode(5))
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
    name = Column(Unicode(30))
    pid = Column(String(20))







