# encoding: utf-8

import mongoengine as db

from shoplifter.catalog.product.model import Product, Variant


db.connect('shoplifter_test')


def setup():
    Variant.drop_collection()
    Product.drop_collection()
