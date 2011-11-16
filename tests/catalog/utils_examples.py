# encoding: utf-8

from shoplifter.catalog.utils import force_unicode, slugify

from ..helpers import *


class ForceUnicodeExamples(object):
    def test_force_unicode_on_unicode(self):
        u = u'some unicôde'
        eq_(force_unicode(u), u)

    def test_force_unicode_on_bytestring(self):
        s = 'some string'
        u = force_unicode(s)

        eq_(u, s)
        is_a_(u, unicode)

    def test_force_unicode_on_object_with_unicode_method(self):
        class A(object):
            __unicode__ = lambda s: u"fdsa"

        a = A()
        u = force_unicode(a)

        eq_(force_unicode(a), u"fdsa")
        is_a_(u, unicode)

    def test_force_unicode_on_object_with_only_str_method(self):
        class A(object):
            __str__ = lambda s: "fdsa"

        a = A()
        u = force_unicode(a)

        eq_(u, u"fdsa")
        is_a_(u, unicode)


def test_slugify():
    def ueq_(a, b):
        eq_(a, b)
        is_a_(a, unicode)

    ueq_(slugify(None), u'')
    ueq_(slugify(''), u'')
    ueq_(slugify('FDSA'), u'fdsa')
    ueq_(slugify('This is a sentence'), u'this-is-a-sentence')
    ueq_(slugify('Thîs is a senténce'), u'this-is-a-sentence')
    ueq_(slugify('Thîs is a senténce', limit=6), u'this-i')
    ueq_(slugify('Thîs is a senténce', limit=7), u'this-is')
    ueq_(slugify('Thîs is a senténce', limit=8), u'this-is')

