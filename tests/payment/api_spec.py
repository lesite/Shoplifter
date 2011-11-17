import mongoengine
import decimal

from shoplifter.core import plugins as core_plugins
from shoplifter.payment.lib.test_helpers import TestOrder
from shoplifter.payment import plugins
from shoplifter.payment import config

from unittest import TestCase
from nose.tools import assert_equals

mongoengine.connect('testdb6')


def get_order(amount=decimal.Decimal('30')):
    return TestOrder(amount)


class PaymentApiSpec(TestCase):
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

    def can_prepare_preauth(self):
        self.load_backend(True)
        order = get_order()
        self.prepare_payment(order, '30')
        assert_equals(order.balance, decimal.Decimal('30'))
        self.assertTrue(order.is_prepared)
        assert_equals(len(order.payment.get_payments()), 1)
        assert_equals(
            order.payment.get_payment_sum(),
            decimal.Decimal('30'))
        assert_equals(
            order.payment.get_prepared_amount(),
            decimal.Decimal('30'))
        assert_equals(
            order.payment.get_captured_amount(),
            decimal.Decimal('0'))
        assert_equals(
            order.payment.get_prepared_and_processed_payment_amount(),
            decimal.Decimal('30'))
        assert_equals(
            order.payment.get_balance(),
            decimal.Decimal('30'))
        assert_equals(
            order.payment.get_to_prepare_amount(),
            decimal.Decimal('0'))

    def can_process_preauth(self):
        self.load_backend(True)
        order = get_order()
        auth = self.prepare_payment(order, '30')
        self.process_payment(auth)
        assert_equals(order.balance, decimal.Decimal('0'))
        self.assertTrue(order.is_prepared)
        assert_equals(len(order.payment.get_payments()), 1)
        assert_equals(
            order.payment.get_payment_sum(),
            decimal.Decimal('30'))
        assert_equals(
            order.payment.get_prepared_amount(),
            decimal.Decimal('0'))
        assert_equals(
            order.payment.get_captured_amount(),
            decimal.Decimal('0'))
        assert_equals(
            order.payment.get_prepared_and_processed_payment_amount(),
            decimal.Decimal('30'))
        assert_equals(
            order.payment.get_balance(),
            decimal.Decimal('0'))
        assert_equals(
            order.payment.get_to_prepare_amount(),
            decimal.Decimal('0'))

    def can_process_multiple_preauth_for_one_order(self):
        self.load_backend(True)
        order = get_order()
        self.prepare_payment(order, '15')
        self.prepare_payment(order, '15')
        order.payment.process_all_payments()
        assert_equals(order.balance, decimal.Decimal('0'))
        self.assertTrue(order.is_prepared)
        assert_equals(len(order.payment.get_payments()), 2)
        assert_equals(
            order.payment.get_payment_sum(),
            decimal.Decimal('30'))
        assert_equals(
            order.payment.get_prepared_amount(),
            decimal.Decimal('0'))
        assert_equals(
            order.payment.get_captured_amount(),
            decimal.Decimal('0'))
        assert_equals(
            order.payment.get_prepared_and_processed_payment_amount(),
            decimal.Decimal('30'))
        assert_equals(
            order.payment.get_balance(),
            decimal.Decimal('0'))
        assert_equals(
            order.payment.get_to_prepare_amount(),
            decimal.Decimal('0'))

    def can_capture_preauth(self):
        self.load_backend(True)
        order = get_order()
        self.prepare_payment(order, '15')
        self.prepare_payment(order, '15')
        order.payment.process_all_payments()
        order.payment.capture_all_authorizations()
        assert_equals(order.balance, decimal.Decimal('0'))
        self.assertTrue(order.is_prepared)
        assert_equals(len(order.payment.get_payments()), 2)
        assert_equals(
            order.payment.get_payment_sum(),
            decimal.Decimal('30'))
        assert_equals(
            order.payment.get_prepared_amount(),
            decimal.Decimal('0'))
        assert_equals(
            order.payment.get_captured_amount(),
            decimal.Decimal('30'))
        assert_equals(
            order.payment.get_prepared_and_processed_payment_amount(),
            decimal.Decimal('30'))
        assert_equals(
            order.payment.get_balance(),
            decimal.Decimal('0'))
        assert_equals(
            order.payment.get_to_prepare_amount(),
            decimal.Decimal('0'))

    def can_perform_one_time_purchase(self):
        self.load_backend(False)
        order = get_order()
        payment = self.prepare_payment(order, '30')
        self.process_payment(payment)
        assert_equals(order.balance, decimal.Decimal('0'))
        self.assertTrue(order.is_prepared)
        assert_equals(len(order.payment.get_payments()), 1)
        assert_equals(
            order.payment.get_payment_sum(),
            decimal.Decimal('30'))
        assert_equals(
            order.payment.get_prepared_amount(),
            decimal.Decimal('0'))
        assert_equals(
            order.payment.get_captured_amount(),
            decimal.Decimal('30'))
        assert_equals(
            order.payment.get_prepared_and_processed_payment_amount(),
            decimal.Decimal('30'))
        assert_equals(
            order.payment.get_balance(),
            decimal.Decimal('0'))
        assert_equals(
            order.payment.get_to_prepare_amount(),
            decimal.Decimal('0'))
