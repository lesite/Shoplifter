# encoding: utf-8

import mongoengine as db

from shoplifter.core import util


class Product(db.Document):
    code = db.StringField(primary_key=True, min_length=3, max_length=30, unique=True)
    name = db.StringField(required=True, min_length=3, max_length=255)
    slug = db.StringField(required=True, min_length=3, max_length=30, unique=True)

    description = db.StringField()
    meta_description = db.StringField()
    meta_keywords = db.StringField()

    available_on = db.DateTimeField()

    # taxclass
    # shipclass

    meta = {
        'indexes': ['slug']
    }

    # url
    # absolute_url

    # inject the util slugify method as a static method
    slugify = staticmethod(util.slugify)

    @classmethod
    def pre_save(cls, sender, document, **kwargs):
        if not document.slug:
            document.slug = cls.slugify(document.name, limit=30)

db.signals.pre_save.connect(Product.pre_save, sender=Product)


class Variant(db.Document):
    product = db.ReferenceField(Product, required=True,
                                reverse_delete_rule=db.DENY)

    sku = db.StringField(primary_key=True, min_length=3, max_length=100, unique=True)
