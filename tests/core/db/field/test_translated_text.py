# encoding: utf-8

from unittest import TestCase
import mongoengine as db

from shoplifter.core.db.field import TranslatedStringField
from shoplifter.core.db.field import TranslatedString
from mongoengine import *
from mongoengine.base import ValidationError
from ludibrio import Stub

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


class TestTanslatedTextOperations(TestCase):
    def setUp(self):
        db.connect(db='mongoenginetest')
        TranslatedDoc.drop_collection()
        doc = TranslatedDoc(text=translated_string)
        doc.save()

    def test_default_values(self):
        doc = TranslatedDoc.objects.all()[0]

        self.assertEqual(unicode(doc.text), translated_string['en'])

    def test_query_translated_string(self):
        en = TranslatedDoc.objects(text__en=u'This is English')
        se = TranslatedDoc.objects(text__se__exists=True)

        self.assertTrue(en.count() == 1)
        self.assertTrue(se.count() == 1)

    def test_query_translated_string_not_found(self):
        fr = TranslatedDoc.objects(text__fr__exists=True)

        self.assertTrue(fr.count() == 0)

    def test_valide_translated_string(self):
        doc = TranslatedDoc.objects.all()[0]

        self.assertTrue(isinstance(doc.text, TranslatedString))
        self.assertEqual(doc.text['se'], translated_string['se'])
