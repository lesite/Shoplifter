from nose.tools import *


def assert_isinstance(inst, cls):
    assert_true(isinstance(inst, cls),
            "{inst} is not of type {cls}".format(inst=inst, cls=cls))

def is_a_(inst, cls):
    assert_isinstance(inst, cls)


