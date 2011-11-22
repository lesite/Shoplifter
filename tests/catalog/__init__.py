# encoding: utf-8

from shoplifter.catalog.product.model import Product, Variant


def setup():
    Variant.drop_collection()
    Product.drop_collection()
