# encoding: utf-8

import mongoengine as db

from shoplifter.catalog import utils


class Product(db.Document):
    code = db.StringField(primary_key=True, min_length=3, max_length=30, unique=True)
    name = db.StringField(required=True, min_length=3, max_length=255)
    slug = db.StringField(required=True, min_length=3, max_length=30, unique=True)
    description = db.StringField()

    meta_description = db.StringField()
    meta_keywords = db.StringField()

    # taxclass
    # shipclass

    meta = {
        'indexes': ['slug']
    }

    # url
    # absolute_url

    # inject the utils.slugify method as a static method
    slugify = staticmethod(utils.slugify)

    @classmethod
    def pre_save(cls, sender, document, **kwargs):
        if not document.slug:
            document.slug = cls.slugify(document.name)

db.signals.pre_save.connect(Product.pre_save, sender=Product)
