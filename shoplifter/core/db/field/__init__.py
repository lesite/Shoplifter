#encoding: utf-8

from mongoengine.fields import DictField
from mongoengine.base import ValidationError
from mongoengine.base import BaseDict

import re


class MissingLanguageFunctionError(Exception):
    pass


def get_lang():
    raise MissingLanguageFunctionError


class TranslatedString(BaseDict):
    def __unicode__(self):
        langs = get_lang()
        if isinstance(langs, basestring):
            return self.get(langs, u"NO TRANSLATION FOUND")
        else:
            for lang in langs:
                if lang in self:
                    return self[lang]

        return u"NO TRANSLATION FOUND"


class TranslatedStringField(DictField):
    """ A locale aware string field     """

    def __init__(self, **kwargs):
        super(TranslatedStringField, self).__init__(**kwargs)

    def __get__(self, instance, owner):
        if instance is None:
            return self
        
        dict_items = instance._data.get(self.name, dict())
        trans_str = TranslatedString(dict_items, instance, self.name)
        return trans_str
