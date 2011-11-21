# encoding: utf-8

import mongoengine

from unittest import TestCase
from shoplifter.payment import config
from shoplifter.core import plugins as core_plugins
from shoplifter.payment.lib.credentials import (
    CreditCard, GiftCard, DebitCard, PaymentCredential)
from nose.tools import assert_equals, assert_raises


mongoengine.connect('testdb6')


class CredentialSpecs(TestCase):
    def setUp(self):
        config.cc_store_time = 60 * 5
        core_plugins.load('temp_storage', 'dummy', None, 'thisisakey123456')
        config.temp_store = core_plugins['temp_storage'].dummy

    def it_fails_when_badly_implemented(self):
        class BadCredential(PaymentCredential):
            pass

        assert_raises(NotImplementedError, BadCredential().get,
                      *('some_id', ))
        assert_raises(NotImplementedError, BadCredential().save)

    def it_fails_when_luhn_fails(self):
        assert_raises(
            PaymentCredential.CardFormatError, 
            CreditCard,
            *('derp1', '4242424242424241'))
        assert_raises(
            PaymentCredential.CardFormatError, 
            DebitCard,
            *('derp1', '4242424242424241'))

    def test_luhn_validation(self):
        # Check that luhn check fails early when instantiating a CC
        badluhn = {
            'transaction_id': 'derp',
            'number': '4530911622722221',
            'exp_year': '2011',
            'exp_month': '07',
            'csc': '770',
            'cc_type': 'V'}

        assert_raises(
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
        assert_equals(cc.number, '4530911622722220')

        # Checks that passing bad key returns None
        cc = CreditCard.get('fail')
        assert_equals(cc, None)
