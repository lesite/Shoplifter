# encoding: utf-8


import mongoengine
import decimal

from unittest import TestCase
from shoplifter.payment import config
from shoplifter.core import plugins as core_plugins
from shoplifter.payment import plugins
from shoplifter.payment.lib.test_helpers import TestOrder
from shoplifter.payment.lib.credentials import CreditCard


mongoengine.connect('testdb6')


def get_order(amount=decimal.Decimal('30')):
    return TestOrder(amount)


class TestApi(TestCase):
    def setUp(self):
        config.cc_store_time = 60 * 5
        core_plugins.load('temp_storage', 'dummy', None, 'thisisakey123456')
        config.temp_store = core_plugins['temp_storage'].dummy

    def prepare_payment(self, order, amount):
        amount = decimal.Decimal(amount)
        pay = self.dummy_backend.prepare_payment(
            order,
            amount,
            '4242424242424242',
            '2011',
            '05',
            csc=123)
        return pay

    def process_payment(self, payment):
        if self.dummy_backend.use_pre_auth:
            self.dummy_backend.authorize(payment)
        else:
            self.dummy_backend.purchase(payment)

    def load_backend(self, use_pre_auth):
        # use_preauth defines whether the backend uses
        # pre-authorization (True) or one-time capture (False).
        plugins.load(
            'payment_backends', 'dummypayment', {'use_pre_auth': use_pre_auth})
        self.dummy_backend = plugins['payment_backends'].dummypayment

    def test_prepare(self):
        self.load_backend(True)
        order = get_order()
        self.prepare_payment(order, '30')
        self.assertEquals(order.balance, decimal.Decimal('30'))
        self.assertTrue(order.is_prepared)
        self.assertEquals(len(order.payment.get_payments()), 1)
        self.assertEquals(
            order.payment.get_payment_sum(),
            decimal.Decimal('30'))
        self.assertEquals(
            order.payment.get_prepared_amount(),
            decimal.Decimal('30'))
        self.assertEquals(
            order.payment.get_captured_amount(),
            decimal.Decimal('0'))
        self.assertEquals(
            order.payment.get_prepared_and_processed_payment_amount(),
            decimal.Decimal('30'))
        self.assertEquals(
            order.payment.get_balance(),
            decimal.Decimal('30'))
        self.assertEquals(
            order.payment.get_to_prepare_amount(),
            decimal.Decimal('0'))

    def test_preauth(self):
        self.load_backend(True)
        order = get_order()
        auth = self.prepare_payment(order, '30')
        self.process_payment(auth)
        self.assertEquals(order.balance, decimal.Decimal('0'))
        self.assertTrue(order.is_prepared)
        self.assertEquals(len(order.payment.get_payments()), 1)
        self.assertEquals(
            order.payment.get_payment_sum(),
            decimal.Decimal('30'))
        self.assertEquals(
            order.payment.get_prepared_amount(),
            decimal.Decimal('0'))
        self.assertEquals(
            order.payment.get_captured_amount(),
            decimal.Decimal('0'))
        self.assertEquals(
            order.payment.get_prepared_and_processed_payment_amount(),
            decimal.Decimal('30'))
        self.assertEquals(
            order.payment.get_balance(),
            decimal.Decimal('0'))
        self.assertEquals(
            order.payment.get_to_prepare_amount(),
            decimal.Decimal('0'))

    def test_payment_processing(self):
        self.load_backend(True)
        order = get_order()
        self.prepare_payment(order, '15')
        self.prepare_payment(order, '15')
        order.payment.process_all_payments()
        self.assertEquals(order.balance, decimal.Decimal('0'))
        self.assertTrue(order.is_prepared)
        self.assertEquals(len(order.payment.get_payments()), 2)
        self.assertEquals(
            order.payment.get_payment_sum(),
            decimal.Decimal('30'))
        self.assertEquals(
            order.payment.get_prepared_amount(),
            decimal.Decimal('0'))
        self.assertEquals(
            order.payment.get_captured_amount(),
            decimal.Decimal('0'))
        self.assertEquals(
            order.payment.get_prepared_and_processed_payment_amount(),
            decimal.Decimal('30'))
        self.assertEquals(
            order.payment.get_balance(),
            decimal.Decimal('0'))
        self.assertEquals(
            order.payment.get_to_prepare_amount(),
            decimal.Decimal('0'))

    def test_auth_capture(self):
        self.load_backend(True)
        order = get_order()
        self.prepare_payment(order, '15')
        self.prepare_payment(order, '15')
        order.payment.process_all_payments()
        order.payment.capture_all_authorizations()
        self.assertEquals(order.balance, decimal.Decimal('0'))
        self.assertTrue(order.is_prepared)
        self.assertEquals(len(order.payment.get_payments()), 2)
        self.assertEquals(
            order.payment.get_payment_sum(),
            decimal.Decimal('30'))
        self.assertEquals(
            order.payment.get_prepared_amount(),
            decimal.Decimal('0'))
        self.assertEquals(
            order.payment.get_captured_amount(),
            decimal.Decimal('30'))
        self.assertEquals(
            order.payment.get_prepared_and_processed_payment_amount(),
            decimal.Decimal('30'))
        self.assertEquals(
            order.payment.get_balance(),
            decimal.Decimal('0'))
        self.assertEquals(
            order.payment.get_to_prepare_amount(),
            decimal.Decimal('0'))

    def test_purchase(self):
        self.load_backend(False)
        order = get_order()
        payment = self.prepare_payment(order, '30')
        self.process_payment(payment)
        self.assertEquals(order.balance, decimal.Decimal('0'))
        self.assertTrue(order.is_prepared)
        self.assertEquals(len(order.payment.get_payments()), 1)
        self.assertEquals(
            order.payment.get_payment_sum(),
            decimal.Decimal('30'))
        self.assertEquals(
            order.payment.get_prepared_amount(),
            decimal.Decimal('0'))
        self.assertEquals(
            order.payment.get_captured_amount(),
            decimal.Decimal('30'))
        self.assertEquals(
            order.payment.get_prepared_and_processed_payment_amount(),
            decimal.Decimal('30'))
        self.assertEquals(
            order.payment.get_balance(),
            decimal.Decimal('0'))
        self.assertEquals(
            order.payment.get_to_prepare_amount(),
            decimal.Decimal('0'))


class TestCC(TestCase):
    def setUp(self):
        config.cc_store_time = 60 * 5
        core_plugins.load('temp_storage', 'dummy', None, 'thisisakey123456')
        config.temp_store = core_plugins['temp_storage'].dummy

    def test_cc(self):
        # Check that luhn check fails early when instantiating a CC
        badluhn = {
            'transaction_id': 'derp',
            'number': '4530911622722221',
            'exp_year': '2011',
            'exp_month': '07',
            'csc': '770',
            'cc_type': 'V'}

        self.assertRaises(
            CreditCard.CardFormatError,
            CreditCard,
            **badluhn)

        # Saves a cc in temp_store
        cc = CreditCard(
            transaction_id='derp',
            number='4530911622722220',
            exp_year='2011',
            exp_month='07',
            csc='770',
            cc_type='V')

        cc.save()

        # Retrieves it and checks it still has data.
        cc = CreditCard.get('derp')
        self.assertEquals(cc.number, '4530911622722220')

        # Checks that passing bad key returns None
        cc = CreditCard.get('fail')
        self.assertEquals(cc, None)


# class TestModels(TestCase):


