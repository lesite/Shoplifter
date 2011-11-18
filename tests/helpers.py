# encoding: utf-8

import mongoengine as db
import functools
from nose.tools import *


assert_invalid = functools.partial(assert_raises, db.ValidationError)


def assert_is_instance(inst, cls):
    assert_true(isinstance(inst, cls),
            u"{inst} is not of type {cls}".format(inst=inst, cls=cls))
