from nose.tools import *


def assert_is_instance(inst, cls):
    assert_true(isinstance(inst, cls),
            u"{inst} is not of type {cls}".format(inst=inst, cls=cls))
