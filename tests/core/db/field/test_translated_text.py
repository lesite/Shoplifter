# encoding: utf-8

from nose.tools import *
import mongoengine as db

from shoplifter.core.db.field import TranslatedStringField
from shoplifter.core.db.field import TranslatedString
from mongoengine import *
from mongoengine.base import ValidationError
from ludibrio import Stub


db.connect(db='mongoenginetest')


def setup():
    TranslatedDoc.drop_collection()
    doc = TranslatedDoc(text=translated_string)
    doc.save()


with Stub() as get_lang:
    from shoplifter.core.db.field import get_lang
    get_lang() >> [u'en', u'se', u'eg']


class TranslatedDoc(db.Document):
    text = TranslatedStringField()


translated_string = dict(
        se=u'Detta är svenska',
        en=u'This is English',
        eg=u'هذه هي اللغة العربية',
    )


class TestTanslatedTextOperations(object):
    def setUp(self):
        pass

    def test_default_values(self):
        doc = TranslatedDoc.objects.all()[0]
        assert_equal(unicode(doc.text), translated_string['en'])

    def test_query_translated_string(self):
        en = TranslatedDoc.objects(text__en=u'This is English')
        se = TranslatedDoc.objects(text__se__exists=True)
        assert_true(en.count() == 1)
        assert_true(se.count() == 1)

    def test_query_translated_string_not_found(self):
        fr = TranslatedDoc.objects(text__fr__exists=True)
        assert_true(fr.count() == 0)

    def test_valide_translated_string(self):
        doc = TranslatedDoc.objects.all()[0]
        assert_true(isinstance(doc.text, TranslatedString))
        assert_equal(doc.text['se'], translated_string['se'])
