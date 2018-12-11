#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import msrptw

setup(

    name='msrptw',
    version=msrptw.__version__,
    description='Collect internet marketing retail price from supermarkets in Taiwan.',

    author='ssivart',
    url='https://github.com/travishen/msrptw/',
    author_email='travishen.tw@gmail.com',
    license='MIT',
    platforms='any',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    packages=find_packages(),
    install_requires=['lxml', 'pathos', 'requests', 'sqlalchemy'],
)