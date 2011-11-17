# encoding: utf-8

import mongoengine

from unittest import TestCase
from shoplifter.payment import config
from shoplifter.core import plugins as core_plugins
from shoplifter.payment.lib.credentials import CreditCard


mongoengine.connect('testdb6')


class CredentialSpecs(TestCase):
    def setUp(self):
        config.cc_store_time = 60 * 5
        core_plugins.load('temp_storage', 'dummy', None, 'thisisakey123456')
        config.temp_store = core_plugins['temp_storage'].dummy

    def test_luhn_validation(self):
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
