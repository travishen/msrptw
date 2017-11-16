#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
from sqlalchemy import create_engine
from contextlib import contextmanager
from . import _base, _session
from .model import Config, Market, Part, Origin

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
            Part(name='全雞'),
            Part(name='雞切塊'),
            Part(name='雞胸肉'),
            Part(name='里肌'),
            Part(name='骨腿'),
            Part(name='腿肉'),
            Part(name='棒腿'),
            Part(name='腿排')
        ]

        pork = Config(name='豬肉')
        pork.parts = [
            Part(name='五花肉'),
            Part(name='梅花肉'),
            Part(name='豬小排'),
            Part(name='里肌肉'),
            Part(name='豬腿肉'),
            Part(name='絞肉'),
            Part(name='肉片'),
            Part(name='肉絲'),
            Part(name='軟骨'),
            Part(name='肋骨'),
            Part(name='排骨')
        ]

        bean = Config(name='豆類')
        bean.parts = [
            Part(name='紅豆'),
            Part(name='黃豆')
        ]

        session.add(chicken)
        session.add(pork)
        session.add(bean)

        geant = Market(name='愛買')
        wellcome = Market(name='頂好')
        rtmart = Market(name='大潤發')
        fengkang = Market(name='楓康')

        session.add(geant)
        session.add(wellcome)
        session.add(rtmart)
        session.add(fengkang)

        tw = Origin(name='台灣')
        au = Origin(name='澳洲')
        us = Origin(name='美國')
        other = Origin(name='其他')

        session.add(tw)
        session.add(au)
        session.add(us)
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


