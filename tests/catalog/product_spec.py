# encoding: utf-8

import mongoengine as db

from nose.tools import *

from shoplifter.catalog.product.model import Product


db.connect('shoplifter_test')


def setup():
    Product.drop_collection()


def create_product(save=True, force_insert=False, **kwargs):
    opts = dict(name='Shoplifter T-Shirt')
    opts.update(kwargs)
    p = Product(**opts)
    if save:
        p.save(force_insert=force_insert)
    return p


class ProductSpec(object):
    def _save_with(self, **kwargs):
        "Resave the Product in self.p with some fields changed."
        for k, v, in kwargs.items():
            setattr(self.p, k, v)
        self.p.save()

    def setup(self):
        create_product(code='SHOPTEE')
        self.p = Product.objects.get(code="SHOPTEE")
    
    def it_is_identified_by_a_unique_code(self):
        assert_equal(self.p.code, self.p.id)

        qs = Product.objects(code='SHOPTEE')
        assert_equal(qs.count(), 1)  # one exists

        p = qs.get()  # get it
        assert_equal(p.code, 'SHOPTEE') # check it

        # test creating again, should not create a new one
        create_product(code="SHOPTEE")
        qs2 = Product.objects(code='SHOPTEE')
        assert_equal(qs2.count(), 1)
        p2 = qs2.get()
        assert_equal(p, p2)

        assert_raises(db.OperationError,
                create_product, code="SHOPTEE", force_insert=True)

    def it_must_have_a_code_between_3_and_30_characters_long(self):
        assert_equal(self.p.code, "SHOPTEE")

        # new name for each new saved product, for unique slug
        def name():
            for i in xrange(10):
                yield str(i) * 3
        name = name()

        # creating new products each time because code is immutable (pk)
        assert_raises(db.ValidationError,
                create_product, code=None,  name=name.next())
        assert_raises(db.ValidationError,
                create_product, code='',    name=name.next())
        assert_raises(db.ValidationError,
                create_product, code='aa',  name=name.next())
        create_product(code='aaa',  name=name.next())
        create_product(code='a'*30, name=name.next())
        assert_raises(db.ValidationError,
                create_product, code='a'*31, name=name.next())
        

    def it_must_have_a_name_between_3_and_255_characters_long(self):
        assert_equal(self.p.name, "Shoplifter T-Shirt")

        assert_raises(db.ValidationError, self._save_with, name=None)
        assert_raises(db.ValidationError, self._save_with, name='')
        assert_raises(db.ValidationError, self._save_with, name='aa')
        assert_raises(db.ValidationError, self._save_with, name='a'*256)

    def it_must_have_a_slug_between_3_and_30_characters_long(self):
        assert_equal(self.p.slug, "shoplifter-t-shirt")
        assert_raises(db.ValidationError, self._save_with, name=None)
        assert_raises(db.ValidationError, self._save_with, name='')
        assert_raises(db.ValidationError, self._save_with, slug='aa')
        assert_raises(db.ValidationError, self._save_with, slug='a'*31)

    def it_should_auto_generate_slug_from_name_when_slug_is_blank(self):
        self._save_with(slug=None)
        assert_equal(self.p.slug, "shoplifter-t-shirt")

        self._save_with(slug='')
        assert_equal(self.p.slug, "shoplifter-t-shirt")

    def it_can_have_a_description(self):
        assert_equal(self.p.description, None)

        self._save_with(description="some description")
        assert_equal(self.p.description, "some description")

    def it_can_have_a_meta_description(self):
        assert_equal(self.p.meta_description, None)

        self._save_with(meta_description="some meta description")
        assert_equal(self.p.meta_description, "some meta description")

    def it_can_have_meta_keywords(self):
        assert_equal(self.p.meta_keywords, None)

        self._save_with(meta_keywords="meta, keywords")
        assert_equal(self.p.meta_keywords, "meta, keywords")

    def it_has_a_static_slugify_method(self):
        assert_equal(Product.slugify(u"Test Slügify"), 'test-slugify')

    def teardown(self):
        Product.objects.delete()
