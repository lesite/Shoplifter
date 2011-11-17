#!/usr/bin/env python
# encoding: utf-8

import os
import sys

from setuptools import setup, find_packages

from shoplifter import release


if sys.version_info < (2, 6):
    raise SystemExit("Python 2.6 or later is required.")


setup(
    name = release.name,
    version = release.version,
    description = release.description,
    author = release.author,
    author_email = release.email,
    url = release.url,
    license = release.license,

    install_requires = [
        'mongoengine',
        'blinker',
        'marrow.util',
        'pycrypto',
        'python-memcached',
    ],

    test_suite='nose.collector',
    tests_require = [
        'nose',
        'coverage',
        'pinocchio==0.2',
        'ludibrio',
    ],

    dependency_links = [
        'https://github.com/lesite/mongoengine/tarball/master#egg=mongoengine',
        'https://github.com/unpluggd/pinocchio/tarball/0.2#egg=pinocchio-0.2',
    ],

    packages = find_packages(exclude=['examples', 'tests']),
    zip_safe = True,
    include_package_data = True,
    package_data = {'': ['README.textile', 'LICENSE']},

    namespace_packages=['shoplifter'],
    entry_points={
        'shoplifter.core.temp_storage': [
            'memcache = shoplifter.core.tempstore:MemcacheStore',
            'dummy = shoplifter.core.tempstore:DummyStore',
        ],
        'shoplifter.payment.payment_backends': [
            'dummypayment = shoplifter.payment.backend.modules:DummyBackend',
            'dummygiftcard = shoplifter.payment.backend.modules:DummyGiftCardBackend',
            'dummydebit = shoplifter.payment.backend.modules:DummyDebitCardBackend',
        ],
    },

    classifiers = [
        "Development Status :: 1 - Planning",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        # TODO: Python 3
        "Topic :: Software Development :: Libraries :: Python Modules",
    ]
)
