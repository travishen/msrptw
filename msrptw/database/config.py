#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
from sqlalchemy import create_engine
from contextlib import contextmanager
from . import _base, _session
from .model import Config, Market, Part, Origin, Alias

engine = None


def setup_session(db_path):
    global engine
    engine = create_engine(db_path)
    _session.configure(bind=engine)


def init():
    print('initializing database...')
    _base.metadata.drop_all(engine)
    _base.metadata.create_all(engine)

    with session_scope() as session:

        chicken = Config(name='雞肉')
        chicken.parts = [
            Part(name='全雞', aliases=[
                Alias(name='大土雞'),
                Alias(name='黃土雞')
            ]),
            Part(name='雞胸肉', aliases=[
                Alias(name='胸肉')
            ]),
            Part(name='雞里肌肉', aliases=[
                Alias(name='里肌')
            ]),
            Part(name='雞骨腿肉', aliases=[
                Alias(name='腿肉'),
                Alias(name='骨腿')
            ]),
            Part(name='雞棒腿肉', aliases=[
                Alias(name='棒棒腿'),
                Alias(name='棒腿')
            ]),
            Part(name='雞腿排肉', aliases=[
                Alias(name='腿排')
            ]),
            Part(name='雞翅(二節)', aliases=[
                Alias(name='二節翅')
            ]),
            Part(name='雞翅(三節)', aliases=[
                Alias(name='三節翅')
            ]),
            Part(name='雞翅腿肉', aliases=[
                Alias(name='翅小腿'),
                Alias(name='翅腿')
            ]),
            Part(name='雞切塊', aliases=[
                Alias(name='切塊')
            ])
        ]

        pork = Config(name='豬肉')
        pork.parts = [
            Part(name='豬腹脇肉', aliases=[
                Alias(name='五花')
            ]),
            Part(name='豬肩胛肉', aliases=[
                Alias(name='梅花')
            ]),
            Part(name='豬肩頸肉', aliases=[
                Alias(name='霜降'),
                Alias(name='松坂'),
                Alias(name='雪花')
            ]),
            Part(name='豬小排', aliases=[
                Alias(name='豬排'),
                Alias(name='豬小排')
            ]),
            Part(name='豬里肌肉', aliases=[
                Alias(name='里肌')
            ]),
            Part(name='豬腿肉', aliases=[
                Alias(name='腿肉'),
                Alias(name='腿'),
                Alias(name='腱子')
            ]),
            Part(name='豬絞肉', aliases=[
                Alias(name='絞肉')
            ]),
            Part(name='豬肉片', aliases=[
                Alias(name='肉片')
            ]),
            Part(name='豬肉絲', aliases=[
                Alias(name='肉絲'),
                Alias(name='肉條'),
            ]),
            Part(name='豬軟骨', aliases=[
                Alias(name='軟骨')
            ]),
            Part(name='豬肋骨', aliases=[
                Alias(name='肋骨')
            ]),
            Part(name='豬排骨', aliases=[
                Alias(name='排骨')
            ])
        ]

        groceries = Config(name='雜貨')
        groceries.parts = [
            Part(name='紅豆'),
            Part(name='黃豆'),
            Part(name='綠豆'),
            Part(name='黑豆'),
            Part(name='枸杞'),
            Part(name='薏仁')
        ]

        veg = Config(name='蔬菜')
        veg.parts = [
            Part(name='玉米筍'),
            Part(name='老薑'),
            Part(name='嫩薑'),
            Part(name='洋蔥'),
            Part(name='紅蘿蔔'),
            Part(name='馬鈴薯'),
            Part(name='小白菜'),
            Part(name='大白菜', aliases=[
                Alias(name='包心白菜')
            ]),
            Part(name='青江菜'),
            Part(name='小黃瓜', aliases=[
                Alias(name='花胡瓜')
            ]),
            Part(name='地瓜葉'),
            Part(name='地瓜'),
            Part(name='青蔥'),
            Part(name='玉米'),
            Part(name='筊白筍'),
            Part(name='芹菜'),
            Part(name='甜椒'),
            Part(name='空心菜'),
            Part(name='茄子'),
            Part(name='杏鮑菇'),
            Part(name='鮮香菇'),
            Part(name='鴻喜菇'),
            Part(name='秀珍菇', aliases=[
                Alias(name='袖珍菇')
            ]),
            Part(name='雪白菇'),
            Part(name='乾香菇'),
            Part(name='三絲菇'),
            Part(name='金絲菇'),
            Part(name='香菇'),
            Part(name='芋頭'),
            Part(name='韭菜'),
            Part(name='高麗菜'),
            Part(name='大蒜'),
            Part(name='木耳'),
            Part(name='大頭菜'),
            Part(name='絲瓜'),
            Part(name='南瓜'),
            Part(name='菠菜'),
            Part(name='茼蒿'),
            Part(name='苦瓜'),
            Part(name='牛蕃茄', aliases=[
                Alias(name='牛番茄')
            ]),
            Part(name='山藥'),
            Part(name='花椰菜', aliases=[
                Alias(name='青花菜')
            ]),
            Part(name='絲瓜'),
            Part(name='豆芽菜', aliases=[
                Alias(name='豆芽')
            ]),
            Part(name='油菜'),
            Part(name='辣椒'),
            Part(name='芥菜'),
            Part(name='莧菜'),
            Part(name='A菜'),
            Part(name='苜蓿芽'),
            Part(name='秋葵'),
            Part(name='香菜'),
            Part(name='九層塔'),
            Part(name='牛蒡'),
            Part(name='胡瓜')
        ]

        fruit = Config(name='水果')
        fruit.parts = [
            Part(name='芭樂'),
            Part(name='檸檬'),
            Part(name='番茄'),
            Part(name='木瓜'),
            Part(name='葡萄'),
            Part(name='鳳梨'),
            Part(name='火龍果'),
            Part(name='梨'),
            Part(name='香蕉'),
            Part(name='百香果'),
            Part(name='柳丁'),
            Part(name='哈密瓜'),
            Part(name='葡萄柚'),
            Part(name='楊桃'),
            Part(name='釋迦'),
            Part(name='椪柑')
        ]

        session.add(chicken)
        session.add(pork)
        session.add(groceries)
        session.add(veg)

        geant = Market(name='愛買')
        wellcome = Market(name='頂好')
        rtmart = Market(name='大潤發')
        fengkang = Market(name='楓康')

        session.add(geant)
        session.add(wellcome)
        session.add(rtmart)
        session.add(fengkang)

        tw = Origin(name='臺灣')
        au = Origin(name='澳洲')
        us = Origin(name='美國')
        cn = Origin(name='中國')
        other = Origin(name='其他')

        session.add(tw)
        session.add(au)
        session.add(us)
        session.add(cn)
        session.add(other)


@contextmanager
def session_scope():
    session = _session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


