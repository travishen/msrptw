#!/usr/bin/env python
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
_session = sessionmaker()
_base = declarative_base()