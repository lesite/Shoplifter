# encoding: utf-8

from nose.tools import *

from shoplifter.catalog.product.model import Product, Variant

from . import db
from .helpers import create_product, create_variant


class VariantSpec(object):
    def setup(self):
        self.code = 'SHOPTEE'
        self.name = 'Shoplifter T-Shirt'

        Product._test_defaults = dict(name=self.name)

        create_product(code=self.code)
        self.p = Product.objects.get(code=self.code)

        Variant._test_defaults = dict(product=self.p)

        self.sku1 = 'STRS001'
        create_variant(product=self.p, sku=self.sku1)
        self.v = Variant.objects.get(sku=self.sku1)

    def it_is_identified_by_a_unique_sku(self):
        assert_equal(self.v.sku, self.v.id)

        assert_equal(Variant.objects(sku=self.sku1).count(), 1)
        create_variant(sku=self.sku1)
        assert_equal(Variant.objects(sku=self.sku1).count(), 1)
        assert_raises(db.OperationError,
                create_variant, sku=self.sku1, force_insert=True)

    def teardown(self):
        Variant.objects.delete()
        Product.objects.delete()
