# encoding: utf-8

from shoplifter.core.util import force_unicode, slugify

from ...helpers import *


def assert_unicode_and_equal(got, expected):
    assert_equal(got, expected)
    assert_is_instance(got, unicode)


class ForceUnicodeExamples(object):
    def test_force_unicode_on_unicode(self):
        u = u'some unicôde'
        assert_unicode_and_equal(force_unicode(u), u)

    def test_force_unicode_on_bytestring(self):
        s = 'some string'
        u = u'some string'

        assert_unicode_and_equal(force_unicode(s), u)

    def test_force_unicode_on_object_with_unicode_method(self):
        class A(object):
            __unicode__ = lambda s: u'fdsa'

        a = A()
        u = u'fdsa'

        assert_unicode_and_equal(force_unicode(a), u)

    def test_force_unicode_on_object_with_only_str_method(self):
        class A(object):
            __str__ = lambda s: 'fdsa'

        a = A()
        u = u'fdsa'

        assert_unicode_and_equal(force_unicode(a), u)


def test_slugify():
    got_and_expected = [
        (slugify(None), u''),
        (slugify(''), u''),
        (slugify('FDSA'), u'fdsa'),
        (slugify('This is a sentence'), u'this-is-a-sentence'),
        (slugify('Thîs is a senténce'), u'this-is-a-sentence'),
        (slugify('Thîs is a senténce', limit=6), u'this-i'),
        (slugify('Thîs is a senténce', limit=7), u'this-is'),
        (slugify('Thîs is a senténce', limit=8), u'this-is'),
    ]

    for got, expected in got_and_expected:
        yield assert_unicode_and_equal, got, expected

