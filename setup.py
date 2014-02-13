#!/usr/bin/env python

import os

try:
    from setuptools import setup, Extension, Command
except ImportError:
    from distutils.core import setup, Extension, Command

import pglet

dependencies = ['tornado', 'momoko']

setup(
    name=pglet.__name__,
    version=pglet.__version__,
    description=pglet.__description__,
    long_description=open('README.rst').read(),
    author=pglet.__author__,
    author_email=pglet.__author_email__,
    url=pglet.__url__,
    license=pglet.__license__,
    packages=['pglet'],
    #test_suite='tests',
    install_requires=dependencies,
    classifiers = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Topic :: Database',
        'Topic :: Database :: Front-Ends'
    ],
    entry_points={
        'console_scripts': [
            'pglet = pglet.__main__:main',
        ],
    }
)
