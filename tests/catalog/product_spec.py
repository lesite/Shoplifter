# encoding: utf-8

from shoplifter.catalog.product.model import Product
from tests.helpers import *
from .. import db
from .helpers import create_product


class ProductSpec(object):
    def resave(self, **kwargs):
        "Resave the Product in self.p with some fields changed."
        for k, v, in kwargs.items():
            setattr(self.p, k, v)
        self.p.save()

    def setup(self):
        self.code = 'SHOPTEE'
        self.name = 'Shoplifter T-Shirt'
        self.slug = 'shoplifter-t-shirt'
        Product._test_defaults = dict(name=self.name)

        create_product(code=self.code)
        self.p = Product.objects.get(code=self.code)
    
    def it_is_identified_by_a_unique_code(self):
        assert_equal(self.p.code, self.p.id)

        assert_equal(Product.objects(code=self.code).count(), 1)
        create_product(code=self.code)
        assert_equal(Product.objects(code=self.code).count(), 1)
        assert_raises(db.OperationError,
                create_product, code=self.code, force_insert=True)

    def it_must_have_a_code_between_3_and_30_characters_long(self):
        assert_equal(self.p.code, self.code)

        # new name for each new saved product, for unique slug
        names = (str(i) * 3 for i in xrange(10))

        assert_invalid(create_product, code=None,  name=names.next())
        assert_invalid(create_product, code='',    name=names.next())
        assert_invalid(create_product, code='aa',  name=names.next())
        create_product(code='aaa',  name=names.next())
        create_product(code='a'*30, name=names.next())
        assert_invalid(create_product, code='a'*31, name=names.next())
        

    def it_must_have_a_name_between_3_and_255_characters_long(self):
        assert_equal(self.p.name, self.name)

        assert_invalid(self.resave, name=None)
        assert_invalid(self.resave, name='')
        assert_invalid(self.resave, name='aa')
        assert_invalid(self.resave, name='a'*256)

    def it_must_have_a_slug_between_3_and_30_characters_long(self):
        assert_equal(self.p.slug, self.slug)
        assert_invalid(self.resave, name=None)
        assert_invalid(self.resave, name='')
        assert_invalid(self.resave, slug='aa')
        assert_invalid(self.resave, slug='a'*31)

    def it_should_auto_generate_slug_from_name_when_slug_is_blank(self):
        self.resave(slug=None)
        assert_equal(self.p.slug, self.slug)

        self.resave(slug='')
        assert_equal(self.p.slug, self.slug)

    def it_can_have_a_description(self):
        assert_equal(self.p.description, None)

        self.resave(description="some description")
        assert_equal(self.p.description, "some description")

    def it_can_have_a_meta_description(self):
        assert_equal(self.p.meta_description, None)

        self.resave(meta_description="some meta description")
        assert_equal(self.p.meta_description, "some meta description")

    def it_can_have_meta_keywords(self):
        assert_equal(self.p.meta_keywords, None)

        self.resave(meta_keywords="meta, keywords")
        assert_equal(self.p.meta_keywords, "meta, keywords")

    def it_has_a_static_slugify_method(self):
        assert_equal(Product.slugify(u"Test Slügify"), 'test-slugify')

    def teardown(self):
        Product.objects.delete()
