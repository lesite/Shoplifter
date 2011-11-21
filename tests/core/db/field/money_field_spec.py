import decimal
import mongoengine
import pymongo
from ....helpers import assert_is_instance

from nose.tools import assert_equals
from shoplifter.core.db.field import MoneyField

mongoengine.connect('mongoenginetest')


class HongZhiBi(mongoengine.Document):
    """
    Default 2 digit precision
    """
    value = MoneyField()


class FiveDecPlacesDoc(mongoengine.Document):
    """
    Bigger precision
    """
    value = MoneyField(decimal_digits=5)


class MoneyFieldSpec(object):
    def get_db(self):
        return pymongo.Connection('127.0.0.1').mongoenginetest

    def get_original(self, mongoengineobj, coll):
        return self.get_db()[coll].find_one(id=mongoengineobj.id)

    def it_takes_in_decimal_but_stores_integer(self):
        doc = HongZhiBi()
        doc.value = decimal.Decimal('100')
        doc.save()
        orig = self.get_original(doc, 'hong_zhi_bi')

        assert_equals(orig['value'], 100 ** 2)

    def it_returns_decimal(self):
        doc = HongZhiBi()
        doc.value = decimal.Decimal('100')
        doc.save()
        doc.reload()

        assert_is_instance(doc.value, decimal.Decimal)

    def its_decimal_place_is_configurable(self):
        doc = FiveDecPlacesDoc()
        doc.value = decimal.Decimal('100.12345')
        doc.save()
        doc.reload()

        orig = self.get_original(doc, 'five_dec_places_doc')

        assert_equals(doc.value, decimal.Decimal('100.12345'))
        assert_equals(orig['value'], 10012345)
