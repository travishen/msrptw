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
                Alias(name='黃土雞'),
                Alias(name='土雞'),
                Alias(name='烏骨雞'),
                Alias(name='古早雞'),
                Alias(name='塊', anti=True),
                Alias(name='胸', anti=True),
                Alias(name='翅', anti=True),
                Alias(name='腿', anti=True)
            ]),
            Part(name='半雞', aliases=[
                Alias(name='半')
            ]),
            Part(name='雞胸肉', aliases=[
                Alias(name='胸肉'),
                Alias(name='雞胸')
            ]),
            Part(name='雞里肌肉', aliases=[
                Alias(name='里肌')
            ]),
            Part(name='雞腿肉', aliases=[
                Alias(name='骨腿'),
                Alias(name='清腿'),
                Alias(name='棒腿'),
                Alias(name='小腿'),
                Alias(name='腿排'),
                Alias(name='去骨雞腿'),
                Alias(name='翅', anti=True)
            ]),
            Part(name='雞翅', aliases=[
                Alias(name='二節翅'),
                Alias(name='三節翅'),
                Alias(name='翅小腿'),
                Alias(name='翅腿')
            ]),
            Part(name='雞切塊', aliases=[
                Alias(name='切塊'),
                Alias(name='剁塊'),
                Alias(name='腿切塊'),
                Alias(name='八塊'),
                Alias(name='九塊')
            ]),
            Part(name='雞雜', aliases=[
                Alias(name='雞肫'),
                Alias(name='雞心'),
                Alias(name='雞尾椎'),
                Alias(name='雞屁股'),
                Alias(name='雞尾椎'),
                Alias(name='雞胗')
            ])
        ]

        pork = Config(name='豬肉')
        pork.parts = [
            Part(name='豬腹脇肉', aliases=[
                Alias(name='五花'),
                Alias(name='三層')
            ]),
            Part(name='豬肩胛肉', aliases=[
                Alias(name='梅花'),
                Alias(name='胛心'),
                Alias(name='胛心排', anti=True)
            ]),
            Part(name='豬肩頸肉', aliases=[
                Alias(name='霜降'),
                Alias(name='松坂'),
                Alias(name='松阪'),
                Alias(name='雪花')
            ]),
            Part(name='豬里肌肉', aliases=[
                Alias(name='里肌'),
                Alias(name='腰內')
            ]),
            Part(name='豬腿肉', aliases=[
                Alias(name='腿肉'),
                Alias(name='腿'),
                Alias(name='腱子'),
                Alias(name='豬蹄膀')
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
            Part(name='豬排骨', aliases=[
                Alias(name='排骨'),
                Alias(name='龍骨'),
                Alias(name='背骨'),
                Alias(name='肋骨'),
                Alias(name='軟骨'),
                Alias(name='大骨'),
                Alias(name='頸骨'),
                Alias(name='胛心排'),
                Alias(name='豬小排')
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
            ]),
            Part(name='昆布'),
            Part(name='乾香菇', aliases=[
                Alias(name='香菇'),
                Alias(name='鈕釦菇')
            ]),
            Part(name='木耳'),
            Part(name='奇亞籽'),
            Part(name='柴魚')
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
                Alias(name='青江白菜'),
                Alias(name='葉白菜'),
                Alias(name='奶油白菜'),
                Alias(name='翠白菜'),
                Alias(name='味美菜'),
                Alias(name='小松菜'),
                Alias(name='青松菜'),
                Alias(name='蚵白菜'),
                Alias(name='蚵仔白菜')
            ]),
            Part(name='結球白菜', aliases=[
                Alias(name='包心白菜'),
                Alias(name='大白菜'),
                Alias(name='娃娃菜')
            ]),
            Part(name='萵苣', aliases=[
                Alias(name='A菜'),
                Alias(name='大陸妹')
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
                Alias(name='蔥頭', anti=True),
                Alias(name='三星蔥')
            ]),
            Part(name='玉米', aliases=[
                Alias(name='玉米筍', anti=True)
            ]),
            Part(name='茭白筍', aliases=[
                Alias(name='筊白筍')
            ]),
            Part(name='芹菜'),
            Part(name='甜椒', aliases=[
                Alias(name='青椒'),
                Alias(name='彩椒')
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
                Alias(name='珊瑚菇'),
                Alias(name='白靈菇'),
                Alias(name='美白菇'),
                Alias(name='金喜菇'),
                Alias(name='金滑菇'),
                Alias(name='舞菇')
            ]),
            Part(name='芋頭'),
            Part(name='韭菜', aliases=[
                Alias(name='韭菜花')
            ]),
            Part(name='韭菜花'),
            Part(name='高麗菜', aliases=[
                Alias(name='高麗菜絲', anti=True),
                Alias(name='脫水', anti=True),
                Alias(name='紫', anti=True),
                Alias(name='甘藍'),
                Alias(name='菜心')
            ]),
            Part(name='紫高麗菜', aliases=[
                Alias(name='高麗菜絲', anti=True),
                Alias(name='脫水', anti=True),
                Alias(name='紫甘藍'),
                Alias(name='紫色甘藍'),
                Alias(name='紫高麗菜'),
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
            Part(name='苦瓜', aliases=[
                Alias(name='青苦瓜'),
                Alias(name='山苦瓜')
            ]),
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
            Part(name='辣椒', aliases=[
                Alias(name='朝天椒'),
                Alias(name='剝皮辣椒'),
                Alias(name='糯米椒')
            ]),
            Part(name='芥菜', aliases=[
                Alias(name='雪菜')
            ]),
            Part(name='莧菜'),
            Part(name='苜蓿芽'),
            Part(name='秋葵'),
            Part(name='香菜', aliases=[
                Alias(name='莞荽')
            ]),
            Part(name='九層塔'),
            Part(name='牛蒡'),
            Part(name='小黃瓜', aliases=[
                Alias(name='花胡瓜')
            ]),
            Part(name='大黃瓜', aliases=[
                Alias(name='胡瓜'),
                Alias(name='刺瓜'),
                Alias(name='黃瓜'),
                Alias(name='小黃瓜', anti=True)
            ]),
            Part(name='蒜頭', aliases=[
                Alias(name='大蒜')
            ]),
            Part(name='紅蔥頭'),
            Part(name='冬瓜'),
            Part(name='洋菇'),
            Part(name='蘆筍'),
            Part(name='甜菜根'),
            Part(name='銀耳'),
            Part(name='水蓮'),
            Part(name='蓮藕'),
            Part(name='蒲瓜', aliases=[
                Alias(name='蒲子'),
                Alias(name='扁浦'),
                Alias(name='扁蒲'),
                Alias(name='瓠瓜'),
                Alias(name='蒲瓜')
            ]),
            Part(name='豌豆', aliases=[
                Alias(name='荷蘭豆'),
                Alias(name='豌豆嬰', anti=True),
                Alias(name='碗豆')
            ]),
            Part(name='四季豆', aliases=[
                Alias(name='敏豆')
            ]),
            Part(name='菜豆', aliases=[
                Alias(name='長豇豆')
            ]),
            Part(name='甜豆'),
            Part(name='豆苗', aliases=[
                Alias(name='豆嬰')
            ]),
            Part(name='芥蘭'),
            Part(name='皇宮菜'),
            Part(name='龍鬚菜'),
            Part(name='山蘇'),
            Part(name='紅鳳菜')
        ]

        fruit = Config(name='水果')
        fruit.parts = [
            Part(name='芭樂', aliases=[
                Alias(name='番石榴')
            ]),
            Part(name='檸檬'),
            Part(name='番茄', aliases=[
                Alias(name='蕃茄')

            ]),
            Part(name='木瓜'),
            Part(name='葡萄'),
            Part(name='鳳梨'),
            Part(name='火龍果'),
            Part(name='梨'),
            Part(name='香蕉'),
            Part(name='百香果'),
            Part(name='柳丁'),
            Part(name='葡萄柚'),
            Part(name='楊桃'),
            Part(name='釋迦'),
            Part(name='椪柑'),
            Part(name='甜柿', aliases=[
                Alias(name='柿')
            ]),
            Part(name='蓮霧'),
            Part(name='橘子', aliases=[
                Alias(name='桔子'),
                Alias(name='柑子')
            ]),
            Part(name='蘋果'),
            Part(name='奇異果'),
            Part(name='甜瓜', aliases=[
                Alias(name='香瓜'),
                Alias(name='洋香瓜'),
                Alias(name='哈蜜瓜'),
                Alias(name='華蜜瓜'),
                Alias(name='哈密瓜'),
                Alias(name='美濃瓜')
            ]),
            Part(name='金桔')
        ]

        session.add(chicken)
        session.add(pork)
        session.add(groceries)
        session.add(veg)
        session.add(fruit)

        g = Market(name='愛買')
        w = Market(name='頂好')
        r = Market(name='大潤發')
        f = Market(name='楓康')
        c = Market(name='家樂福')
        b = Market(name='濱江')
        n = Market(name='新北市農產中心')

        session.add(g)
        session.add(w)
        session.add(r)
        session.add(f)
        session.add(c)
        session.add(b)
        session.add(n)

        tw = Origin(name='臺灣')
        au = Origin(name='澳洲')
        us = Origin(name='美國')
        cn = Origin(name='中國')
        jp = Origin(name='日本')
        kr = Origin(name='韓國')
        other = Origin(name='其他')

        session.add(tw)
        session.add(au)
        session.add(us)
        session.add(cn)
        session.add(jp)
        session.add(kr)
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


