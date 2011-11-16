import random
from mongoengine import Document
from shoplifter.payment.api import PayableOrder


class DummyAddress(object):
    """
    A dummy Address.
    """
    first_name = 'Benoit'
    last_name = 'C. Doe'
    email = 'bendoe@example.com'
    phone_number = '5146593328'
    street_number = '55'
    street_name = 'Derpy'
    street_type = 'Ave'
    unit_number = '730'
    street_direction = 'W'
    street_line_2 = 'rr 2'
    postal_code = 'H2T1N6'
    city = 'Montreal'
    province = 'QC'
    country = 'CA'


class TestOrder(PayableOrder):
    """
    This is basically, over time, making assumptions on some of
    order's behaviours and attributes, though it's only used for
    testing here.
    """

    # TODO
    # Maybe this whould be a "Payable" interface of some
    # sort.. and orders can subclass the main class.

    def __init__(self, total):
        self.total = total
        self.id = str(random.randint(99999, 10000000))
        super(TestOrder, self).__init__()

    billing = DummyAddress()
    shipping = DummyAddress()
