#encoding: utf-8

import decimal

from mongoengine.fields import DictField, IntField
from mongoengine.base import BaseDict


class MissingLanguageFunctionError(Exception):
    pass


def get_lang(): # pragma: no cover
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
    
    def __str__(self):
        return self.__unicode__()


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


class MoneyField(IntField):
    """
    This is actually an integer field that stores the number of
    cents. This can be used when we need to store precise money
    amounts that cannot afford to lose precision.
    Pros: This supports database operations like sum
    """

    def __init__(
        self, min_value=None, max_value=None, decimal_digits=2, **kwargs):
        self.min_value, self.max_value, self.decimal_digits = \
            min_value, max_value, decimal_digits
        super(MoneyField, self).__init__(**kwargs)

    def aggregate_to_python(self, value):
        return self.to_python(value)

    def to_python(self, value):
        return decimal.Decimal(str(value)) / (10 ** self.decimal_digits)

    def to_mongo(self, value):
        return int(
            (value * (10 ** self.decimal_digits)).to_integral())
