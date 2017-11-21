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
                Alias(name='骨腿')
            ]),
            Part(name='雞清腿肉', aliases=[
                Alias(name='清腿')
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
                Alias(name='切塊'),
                Alias(name='剁塊'),
                Alias(name='腿切塊')
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
                Alias(name='肉片'),
                Alias(name='薄片')
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
            Part(name='紅豆', aliases=[
                Alias(name='豆仁', anti=True),
                Alias(name='大紅豆', anti=True),
                Alias(name='紅豆薏仁', anti=True)
            ]),
            Part(name='黃豆', aliases=[
                Alias(name='豆仁', anti=True),
                Alias(name='豆仁', anti=True)
            ]),
            Part(name='綠豆', aliases=[
                Alias(name='豆仁', anti=True),
                Alias(name='豆仁', anti=True)
            ]),
            Part(name='黑豆', aliases=[
                Alias(name='豆仁', anti=True),
                Alias(name='黑豆豉', anti=True)
            ]),
            Part(name='花豆', aliases=[
                Alias(name='大紅豆', anti=True)
            ]),
            Part(name='薏仁', aliases=[
                Alias(name='大薏仁'),
                Alias(name='紅豆薏仁', anti=True)
            ]),
            Part(name='其他雜糧', aliases=[
                Alias(name='蓮子'),
                Alias(name='小米'),
                Alias(name='粉圓'),
                Alias(name='芝麻'),
                Alias(name='西谷米'),
                Alias(name='糯米'),
                Alias(name='藜麥'),
                Alias(name='枸杞'),
                Alias(name='麥仁'),
                Alias(name='紅豆薏仁')
            ]),
            Part(name='花生', aliases=[
                Alias(name='土豆')
            ])
        ]

        veg = Config(name='蔬菜')
        veg.parts = [
            Part(name='玉米筍'),
            Part(name='薑'),
            Part(name='洋蔥'),
            Part(name='蘿蔔', aliases=[
                Alias(name='紅蘿蔔', anti=True),
                Alias(name='胡蘿蔔', anti=True),
                Alias(name='菜頭')
            ]),
            Part(name='紅蘿蔔', aliases=[
                Alias(name='胡蘿蔔')
            ]),
            Part(name='馬鈴薯'),
            Part(name='不結球白菜', aliases=[
                Alias(name='小白菜'),
                Alias(name='青江菜'),
                Alias(name='葉白菜'),
                Alias(name='奶油白菜')
            ]),

            Part(name='結球白菜', aliases=[
                Alias(name='包心白菜'),
                Alias(name='大白菜'),
                Alias(name='娃娃菜')
            ]),
            Part(name='芥藍', aliases=[
                Alias(name='格藍菜'),
                Alias(name='格蘭菜')
            ]),
            Part(name='地瓜葉'),
            Part(name='地瓜', aliases=[
                Alias(name='地瓜葉', anti=True)
            ]),
            Part(name='青蔥', aliases=[
                Alias(name='蔥')
            ]),
            Part(name='玉米', aliases=[
                Alias(name='玉米筍', anti=True)
            ]),
            Part(name='茭白筍'),
            Part(name='芹菜'),
            Part(name='甜椒', aliases=[
                Alias(name='青椒')
            ]),
            Part(name='空心菜', aliases=[
                Alias(name='蕹菜')
            ]),
            Part(name='茄子'),
            Part(name='杏鮑菇'),
            Part(name='香菇', aliases=[
                Alias(name='乾香菇', anti=True)
            ]),
            Part(name='乾香菇'),
            Part(name='金針菇'),
            Part(name='其他食用菇', aliases=[
                Alias(name='雪白菇'),
                Alias(name='金絲菇'),
                Alias(name='三絲菇'),
                Alias(name='雨來菇'),
                Alias(name='白玉菇'),
                Alias(name='黑美人菇'),
                Alias(name='白精靈菇'),
                Alias(name='真珠菇'),
                Alias(name='秀珍菇'),
                Alias(name='袖珍菇'),
                Alias(name='鴻喜菇'),
                Alias(name='珊瑚菇')
            ]),
            Part(name='芋頭'),
            Part(name='韭菜'),
            Part(name='高麗菜', aliases=[
                Alias(name='高麗菜絲', anti=True),
                Alias(name='甘藍')
            ]),
            Part(name='木耳'),
            Part(name='大頭菜'),
            Part(name='絲瓜', aliases=[
                Alias(name='菜瓜'),
                Alias(name='角瓜'),
            ]),
            Part(name='南瓜'),
            Part(name='菠菜', aliases=[
                Alias(name='菠菱菜'),
                Alias(name='菠薐菜'),
            ]),
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
            Part(name='香菜', aliases=[
                Alias(name='莞荽')
            ]),
            Part(name='九層塔'),
            Part(name='牛蒡'),
            Part(name='胡瓜', aliases=[
                Alias(name='小黃瓜')
            ]),
            Part(name='蒜頭', aliases=[
                Alias(name='大蒜')
            ]),
            Part(name='冬瓜'),
            Part(name='洋菇'),
            Part(name='蘆筍'),
            Part(name='甜菜根'),
            Part(name='銀耳'),
            Part(name='水蓮'),
            Part(name='扁蒲', aliases=[
                Alias(name='蒲子')
            ]),
            Part(name='豌豆', aliases=[
                Alias(name='荷蘭豆')
            ]),
            Part(name='四季豆', aliases=[
                Alias(name='敏豆')
            ]),
            Part(name='菜豆', aliases=[
                Alias(name='長豇豆')
            ]),
            Part(name='豆苗')
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
            Part(name='哈密瓜', aliases=[
                Alias(name='洋香瓜')
            ]),
            Part(name='葡萄柚'),
            Part(name='楊桃'),
            Part(name='釋迦'),
            Part(name='椪柑'),
            Part(name='甜柿', aliases=[
                Alias(name='柿')
            ])
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


