import mongoengine
import decimal

from shoplifter.core import plugins as core_plugins
from shoplifter.payment.lib.test_helpers import TestOrder
from shoplifter.payment import plugins
from shoplifter.payment import config
from shoplifter.payment.models import (
    Authorization, Payment, Addressee, BaseTransaction)
from shoplifter.payment.backend import BaseBackend
from shoplifter.payment.backend.modules.dummy import TransactionTypeNotSupported

from nose.tools import assert_equals, assert_raises

mongoengine.connect('testdb6')


def get_order(amount=decimal.Decimal('30')):
    return TestOrder(amount)


class TestAddressee(object):
    def it_gets_an_address_from_order_if_available(self):
        order = get_order()
        addressee = Addressee.from_order_address(order.billing)
        assert_equals(addressee.first_name, 'Benoit')
        order.billing = None
        addressee = Addressee.from_order_address(order.billing)
        assert(not addressee)


class BackendPaymentApiSpec(object):

    def setup(self):
        config.cc_store_time = 60 * 5
        core_plugins.load('temp_storage', 'dummy', None, 'thisisakey123456')
        config.temp_store = core_plugins['temp_storage'].dummy

    def prepare_payment(self, order, amount):
        amount = decimal.Decimal(amount)

        if self.backend.name == 'dummypayment':
            args = (
                order,
                amount,
                '4242424242424242',
                '2011',
                '05',)
            kwargs = {
                'csc': 123}

        elif self.backend.name == 'dummygiftcard':
            args = (
                order,
                amount,
                '4242424242424242')
            kwargs = {}

        elif self.backend.name == 'dummydebit':
            args = (
                order,
                amount,
                '4242424242424242')
            kwargs = {}

        pay = self.backend.prepare_payment(*args, **kwargs)
        return pay

    def load_backend(self, use_pre_auth, plugin='dummypayment'):
        # use_preauth defines whether the backend uses
        # pre-authorization (True) or one-time capture (False).
        plugins.load(
            'payment_backends', plugin, {'use_pre_auth': use_pre_auth})
        self.backend = plugins['payment_backends'][plugin]

    def test_second_capture_fail(self):
        """
        The second attemps at an authorization capture fails if a
        capture was already attempted but 'processed' was never set to
        True. This can be overidden using force_capture argument in
        capture_all_authorizations.
        """

        self.load_backend(True)
        order = get_order()
        auth = self.prepare_payment(order, '30')
        auth.process()
        auth.create_capture(
            self.backend.gen_transaction_id(order.id),
            decimal.Decimal('30'),
            'dummypayment')

        assert_raises(
            self.backend.CaptureAlreadyExists,
            order.payment.capture_all_authorizations)

        order.payment.capture_all_authorizations(force_capture=True)
        assert_equals(
            order.payment.get_captured_amount(), decimal.Decimal('30'))

    def test_second_capture_fail_giftcard(self):
        """
        Second attemp with unprocessed capture, but when using GiftCard.
        """

        self.load_backend(True, 'dummygiftcard')
        order = get_order()
        auth = self.prepare_payment(order, '30')
        auth.process()
        auth.create_capture(
            self.backend.gen_transaction_id(order.id),
            decimal.Decimal('30'),
            'dummypayment')

        assert_raises(
            self.backend.CaptureAlreadyExists,
            order.payment.capture_all_authorizations)

        order.payment.capture_all_authorizations(force_capture=True)
        assert_equals(
            order.payment.get_captured_amount(), decimal.Decimal('30'))

    def test_transaction_fails_when_badly_implemented(self):
        class BadBackend(BaseTransaction):
            pass

        assert_raises(NotImplementedError, BadBackend().process)

    def it_fails_authorizing_when_cc_not_in_cache(self):
        self.load_backend(True)
        order = get_order()
        auth = self.prepare_payment(order, '30')

        # Excplicitly delete the key from temp store.
        config.temp_store.delete(auth.transaction_id)

        # Now processing fails.
        assert_raises(
            self.backend.WaitedTooLong,
            auth.process)

    def it_fails_purchasing_when_cc_not_in_cache(self):
        self.load_backend(False)
        order = get_order()
        auth = self.prepare_payment(order, '30')

        # Excplicitly delete the key from temp store.
        config.temp_store.delete(auth.transaction_id)

        # Now processing fails.
        assert_raises(
            self.backend.WaitedTooLong,
            auth.process)

    def it_fails_authorizing_when_cc_not_in_cache_giftcard(self):
        self.load_backend(True, 'dummygiftcard')
        order = get_order()
        auth = self.prepare_payment(order, '30')

        # Excplicitly delete the key from temp store.
        config.temp_store.delete(auth.transaction_id)

        # Now processing fails.
        assert_raises(
            self.backend.WaitedTooLong,
            auth.process)

    def it_fails_purchasing_when_cc_not_in_cache_giftcard(self):
        self.load_backend(False, 'dummygiftcard')
        order = get_order()
        auth = self.prepare_payment(order, '30')

        # Excplicitly delete the key from temp store.
        config.temp_store.delete(auth.transaction_id)

        # Now processing fails.
        assert_raises(
            self.backend.WaitedTooLong,
            auth.process)

    def it_fails_when_trying_to_authorize_debit(self):
        self.load_backend(True, 'dummydebit')
        order = get_order()
        auth = self.prepare_payment(order, '30')

        # Now processing fails.
        assert_raises(TransactionTypeNotSupported, auth.process)

    def it_fails_purchasing_when_cc_not_in_cache_debitcard(self):
        self.load_backend(False, 'dummydebit')
        order = get_order()
        auth = self.prepare_payment(order, '30')

        # Excplicitly delete the key from temp store.
        config.temp_store.delete(auth.transaction_id)

        # Now processing fails.
        assert_raises(
            self.backend.WaitedTooLong,
            auth.process)

    def it_fails_when_backend_badly_implemented(self):
        class BadBackend(BaseBackend):
            pass
        sample_conf = {'use_pre_auth': False}
        assert_raises(NotImplementedError, BadBackend(sample_conf).purchase, *(None, ))
        assert_raises(NotImplementedError, BadBackend(sample_conf).authorize, *(None, ))
        assert_raises(NotImplementedError, BadBackend(sample_conf).confirm, *(None, ))
        assert_raises(NotImplementedError, BadBackend(sample_conf).cancel, *(None, ))
        assert_raises(NotImplementedError, BadBackend(sample_conf).refund, *(None, ))

    def it_doesnt_need_an_address_to_process_an_order(self):
        self.load_backend(True)
        order = get_order()
        order.billing = None
        order.shipping = None
        self.prepare_payment(order, '15')
        self.prepare_payment(order, '15')
        order.payment.process_all_payments()
        order.payment.capture_all_authorizations()
        assert_equals(order.balance, decimal.Decimal('0'))
        assert(order.is_prepared)
        assert_equals(len(order.payment.get_payments()), 2)
        assert_equals(order.payment.get_payment_sum(), decimal.Decimal('30'))
        assert_equals(order.payment.get_prepared_amount(), decimal.Decimal('0'))
        assert_equals(order.payment.get_captured_amount(), decimal.Decimal('30'))
        assert_equals(order.payment.get_prepared_and_processed_payment_amount(), decimal.Decimal('30'))
        assert_equals(order.payment.get_balance(), decimal.Decimal('0'))
        assert_equals(order.payment.get_to_prepare_amount(), decimal.Decimal('0'))

    def can_prepare_preauth(self):
        self.load_backend(True)
        order = get_order()
        self.prepare_payment(order, '30')
        assert_equals(order.balance, decimal.Decimal('30'))
        assert(order.is_prepared)
        assert_equals(len(order.payment.get_payments()), 1)
        assert_equals(order.payment.get_payment_sum(), decimal.Decimal('30'))
        assert_equals(order.payment.get_prepared_amount(), decimal.Decimal('30'))
        assert_equals(order.payment.get_captured_amount(), decimal.Decimal('0'))
        assert_equals(order.payment.get_prepared_and_processed_payment_amount(), decimal.Decimal('30'))
        assert_equals(order.payment.get_balance(), decimal.Decimal('30'))
        assert_equals(order.payment.get_to_prepare_amount(), decimal.Decimal('0'))

    def can_process_preauth(self):
        self.load_backend(True)
        order = get_order()
        auth = self.prepare_payment(order, '30')
        auth.process()
        assert_equals(order.balance, decimal.Decimal('0'))
        assert(order.is_prepared)
        assert_equals(len(order.payment.get_payments()), 1)
        assert_equals(order.payment.get_payment_sum(), decimal.Decimal('30'))
        assert_equals(order.payment.get_prepared_amount(), decimal.Decimal('0'))
        assert_equals(order.payment.get_captured_amount(), decimal.Decimal('0'))
        assert_equals(order.payment.get_prepared_and_processed_payment_amount(), decimal.Decimal('30'))
        assert_equals(order.payment.get_balance(), decimal.Decimal('0'))
        assert_equals(order.payment.get_to_prepare_amount(), decimal.Decimal('0'))

    def can_process_multiple_preauth_for_one_order(self):
        self.load_backend(True)
        order = get_order()
        self.prepare_payment(order, '15')
        self.prepare_payment(order, '15')
        order.payment.process_all_payments()
        assert_equals(order.balance, decimal.Decimal('0'))
        assert(order.is_prepared)
        assert_equals(len(order.payment.get_payments()), 2)
        assert_equals(order.payment.get_payment_sum(), decimal.Decimal('30'))
        assert_equals(order.payment.get_prepared_amount(), decimal.Decimal('0'))
        assert_equals(order.payment.get_captured_amount(), decimal.Decimal('0'))
        assert_equals(order.payment.get_prepared_and_processed_payment_amount(), decimal.Decimal('30'))
        assert_equals(order.payment.get_balance(), decimal.Decimal('0'))
        assert_equals(order.payment.get_to_prepare_amount(), decimal.Decimal('0'))

    def can_capture_preauth(self):
        self.load_backend(True)
        order = get_order()
        self.prepare_payment(order, '15')
        self.prepare_payment(order, '15')
        order.payment.process_all_payments()
        order.payment.capture_all_authorizations()
        assert_equals(order.balance, decimal.Decimal('0'))
        assert(order.is_prepared)
        assert_equals(len(order.payment.get_payments()), 2)
        assert_equals(order.payment.get_payment_sum(), decimal.Decimal('30'))
        assert_equals(order.payment.get_prepared_amount(), decimal.Decimal('0'))
        assert_equals(order.payment.get_captured_amount(), decimal.Decimal('30'))
        assert_equals(order.payment.get_prepared_and_processed_payment_amount(), decimal.Decimal('30'))
        assert_equals(order.payment.get_balance(), decimal.Decimal('0'))
        assert_equals(order.payment.get_to_prepare_amount(), decimal.Decimal('0'))


    def can_confirm_lesser_amount(self):
        self.load_backend(True)
        order = get_order()

        auth1 = self.prepare_payment(order, '15')
        auth2 = self.prepare_payment(order, '15')
        assert(order.is_prepared)

        order.payment.process_all_payments()

        assert_equals(len(order.payment.get_payments(processed=True, success=True)), 2)

        auth1.reload()
        auth2.reload()
        self.backend.confirm(auth1, decimal.Decimal('0.09'))
        self.backend.confirm(auth2, decimal.Decimal('7.51'))

        assert_equals(order.balance, decimal.Decimal('0'))
        assert_equals(len(order.payment.get_payments()), 2)
        assert_equals(order.payment.get_payment_sum(), decimal.Decimal('30'))
        assert_equals(order.payment.get_prepared_amount(), decimal.Decimal('0'))
        assert_equals(order.payment.get_captured_amount(), decimal.Decimal('7.60'))
        assert_equals(order.payment.get_prepared_and_processed_payment_amount(),decimal.Decimal('30'))
        assert_equals(order.payment.get_balance(), decimal.Decimal('0'))
        assert_equals(order.payment.get_to_prepare_amount(), decimal.Decimal('0'))

    def can_automatically_find_the_amount(self):
        self.load_backend(True)
        order = get_order()
        p1 = self.prepare_payment(order, '30')

        order.payment.process_all_payments()

        p1.reload()
        self.backend.confirm(p1)
        assert_equals(order.balance, decimal.Decimal('0'))
        assert(order.is_prepared)
        assert_equals(len(order.payment.get_payments()), 1)
        assert_equals(order.payment.get_payment_sum(), decimal.Decimal('30'))
        assert_equals(order.payment.get_prepared_amount(), decimal.Decimal('0'))
        assert_equals(order.payment.get_captured_amount(), decimal.Decimal('30'))
        assert_equals(order.payment.get_prepared_and_processed_payment_amount(), decimal.Decimal('30'))
        assert_equals(order.payment.get_balance(), decimal.Decimal('0'))
        assert_equals(order.payment.get_to_prepare_amount(), decimal.Decimal('0'))

    def can_perform_one_time_purchase(self):
        self.load_backend(False)
        order = get_order()
        payment = self.prepare_payment(order, '30')
        payment.process()
        assert_equals(order.balance, decimal.Decimal('0'))
        assert(order.is_prepared)
        assert_equals(len(order.payment.get_payments()), 1)
        assert_equals(order.payment.get_payment_sum(), decimal.Decimal('30'))
        assert_equals(order.payment.get_prepared_amount(), decimal.Decimal('0'))
        assert_equals(order.payment.get_captured_amount(), decimal.Decimal('30'))
        assert_equals(order.payment.get_prepared_and_processed_payment_amount(), decimal.Decimal('30'))
        assert_equals(order.payment.get_balance(), decimal.Decimal('0'))
        assert_equals(order.payment.get_to_prepare_amount(), decimal.Decimal('0'))

    def can_prepare_preauth_giftcard(self):
        self.load_backend(True, 'dummygiftcard')
        order = get_order()
        self.prepare_payment(order, '30')
        assert_equals(order.balance, decimal.Decimal('30'))
        assert(order.is_prepared)
        assert_equals(len(order.payment.get_payments()), 1)
        assert_equals(order.payment.get_payment_sum(), decimal.Decimal('30'))
        assert_equals(order.payment.get_prepared_amount(), decimal.Decimal('30'))
        assert_equals(order.payment.get_captured_amount(), decimal.Decimal('0'))
        assert_equals(order.payment.get_prepared_and_processed_payment_amount(), decimal.Decimal('30'))
        assert_equals(order.payment.get_balance(), decimal.Decimal('30'))
        assert_equals(order.payment.get_to_prepare_amount(), decimal.Decimal('0'))

    def can_process_preauth_giftcard(self):
        self.load_backend(True, 'dummygiftcard')
        order = get_order()
        auth = self.prepare_payment(order, '30')
        auth.process()
        assert_equals(order.balance, decimal.Decimal('0'))
        assert(order.is_prepared)
        assert_equals(len(order.payment.get_payments()), 1)
        assert_equals(order.payment.get_payment_sum(), decimal.Decimal('30'))
        assert_equals(order.payment.get_prepared_amount(), decimal.Decimal('0'))
        assert_equals(order.payment.get_captured_amount(), decimal.Decimal('0'))
        assert_equals(order.payment.get_prepared_and_processed_payment_amount(), decimal.Decimal('30'))
        assert_equals(order.payment.get_balance(), decimal.Decimal('0'))
        assert_equals(order.payment.get_to_prepare_amount(), decimal.Decimal('0'))

    def can_process_multiple_preauth_for_one_order_giftcard(self):
        self.load_backend(True, 'dummygiftcard')
        order = get_order()
        self.prepare_payment(order, '15')
        self.prepare_payment(order, '15')
        order.payment.process_all_payments()
        assert_equals(order.balance, decimal.Decimal('0'))
        assert(order.is_prepared)
        assert_equals(len(order.payment.get_payments()), 2)
        assert_equals(order.payment.get_payment_sum(), decimal.Decimal('30'))
        assert_equals(order.payment.get_prepared_amount(), decimal.Decimal('0'))
        assert_equals(order.payment.get_captured_amount(), decimal.Decimal('0'))
        assert_equals(order.payment.get_prepared_and_processed_payment_amount(), decimal.Decimal('30'))
        assert_equals(order.payment.get_balance(), decimal.Decimal('0'))
        assert_equals(order.payment.get_to_prepare_amount(), decimal.Decimal('0'))

    def can_capture_preauth_giftcard(self):
        self.load_backend(True, 'dummygiftcard')
        order = get_order()
        self.prepare_payment(order, '15')
        self.prepare_payment(order, '15')
        order.payment.process_all_payments()
        order.payment.capture_all_authorizations()
        assert_equals(order.balance, decimal.Decimal('0'))
        assert(order.is_prepared)
        assert_equals(len(order.payment.get_payments()), 2)
        assert_equals(order.payment.get_payment_sum(), decimal.Decimal('30'))
        assert_equals(order.payment.get_prepared_amount(), decimal.Decimal('0'))
        assert_equals(order.payment.get_captured_amount(), decimal.Decimal('30'))
        assert_equals(order.payment.get_prepared_and_processed_payment_amount(), decimal.Decimal('30'))
        assert_equals(order.payment.get_balance(), decimal.Decimal('0'))
        assert_equals(order.payment.get_to_prepare_amount(), decimal.Decimal('0'))


    def can_confirm_lesser_amount_giftcard(self):
        self.load_backend(True, 'dummygiftcard')
        order = get_order()

        auth1 = self.prepare_payment(order, '15')
        auth2 = self.prepare_payment(order, '15')
        assert(order.is_prepared)

        order.payment.process_all_payments()

        assert_equals(len(order.payment.get_payments(processed=True, success=True)), 2)

        auth1.reload()
        auth2.reload()
        self.backend.confirm(auth1, decimal.Decimal('0.09'))
        self.backend.confirm(auth2, decimal.Decimal('7.51'))

        assert_equals(order.balance, decimal.Decimal('0'))
        assert_equals(len(order.payment.get_payments()), 2)
        assert_equals(order.payment.get_payment_sum(), decimal.Decimal('30'))
        assert_equals(order.payment.get_prepared_amount(), decimal.Decimal('0'))
        assert_equals(order.payment.get_captured_amount(), decimal.Decimal('7.60'))
        assert_equals(order.payment.get_prepared_and_processed_payment_amount(),decimal.Decimal('30'))
        assert_equals(order.payment.get_balance(), decimal.Decimal('0'))
        assert_equals(order.payment.get_to_prepare_amount(), decimal.Decimal('0'))

    def can_automatically_find_the_amount_giftcard(self):
        self.load_backend(True, 'dummygiftcard')
        order = get_order()
        p1 = self.prepare_payment(order, '30')

        order.payment.process_all_payments()

        p1.reload()
        self.backend.confirm(p1)
        assert_equals(order.balance, decimal.Decimal('0'))
        assert(order.is_prepared)
        assert_equals(len(order.payment.get_payments()), 1)
        assert_equals(order.payment.get_payment_sum(), decimal.Decimal('30'))
        assert_equals(order.payment.get_prepared_amount(), decimal.Decimal('0'))
        assert_equals(order.payment.get_captured_amount(), decimal.Decimal('30'))
        assert_equals(order.payment.get_prepared_and_processed_payment_amount(), decimal.Decimal('30'))
        assert_equals(order.payment.get_balance(), decimal.Decimal('0'))
        assert_equals(order.payment.get_to_prepare_amount(), decimal.Decimal('0'))

    def can_perform_one_time_purchase_giftcard(self):
        self.load_backend(False, 'dummygiftcard')
        order = get_order()
        payment = self.prepare_payment(order, '30')
        payment.process()
        assert_equals(order.balance, decimal.Decimal('0'))
        assert(order.is_prepared)
        assert_equals(len(order.payment.get_payments()), 1)
        assert_equals(order.payment.get_payment_sum(), decimal.Decimal('30'))
        assert_equals(order.payment.get_prepared_amount(), decimal.Decimal('0'))
        assert_equals(order.payment.get_captured_amount(), decimal.Decimal('30'))
        assert_equals(order.payment.get_prepared_and_processed_payment_amount(), decimal.Decimal('30'))
        assert_equals(order.payment.get_balance(), decimal.Decimal('0'))
        assert_equals(order.payment.get_to_prepare_amount(), decimal.Decimal('0'))

    def can_perform_one_time_purchase_debitcard(self):
        self.load_backend(False, 'dummydebit')
        order = get_order()
        payment = self.prepare_payment(order, '30')
        payment.process()
        assert_equals(order.balance, decimal.Decimal('0'))
        assert(order.is_prepared)
        assert_equals(len(order.payment.get_payments()), 1)
        assert_equals(order.payment.get_payment_sum(), decimal.Decimal('30'))
        assert_equals(order.payment.get_prepared_amount(), decimal.Decimal('0'))
        assert_equals(order.payment.get_captured_amount(), decimal.Decimal('30'))
        assert_equals(order.payment.get_prepared_and_processed_payment_amount(), decimal.Decimal('30'))
        assert_equals(order.payment.get_balance(), decimal.Decimal('0'))
        assert_equals(order.payment.get_to_prepare_amount(), decimal.Decimal('0'))
