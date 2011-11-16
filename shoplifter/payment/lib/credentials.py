import shoplifter.payment
from shoplifter.payment import config


class PaymentCredential(object):

    class CardFormatError(Exception):
        pass

    def is_luhn_valid(self):
        """
        This checks that the CC number validates against the luhn
        algorithm. Code taken from
        http://en.wikipedia.org/wiki/Luhn_algorithm
        """
        num = map(int, self.number)
        return sum(num[::-2] + [
                sum(divmod(d * 2, 10)) for d in num[-2::-2]]) % 10 == 0

    @staticmethod
    def get(self, transaction_id):
        raise NotImplementedError

    def save(self):
        raise NotImplementedError


class GiftCard(PaymentCredential):
    """
    This is used to store gift card credentials.
    """
    def __init__(self, transaction_id, number):
        self.transaction_id = str(transaction_id)
        self.number = number

    @staticmethod
    def get(transaction_id):
        gc = config.temp_store.get(transaction_id)
        if not gc:
            return None
        return GiftCard(
            transaction_id,
            gc['number'],
            )

    def save(self):
        to = config.cc_store_time
        key = self.transaction_id
        gc = {
            'number': self.number,
            }
        config.temp_store.store(key, gc, to, encrypted=True)


class CreditCard(PaymentCredential):
    """
    This is the CreditCard class definition. It's not a mongoengine
    data model but rather it stores its data encrypted in the
    tempstore, hence the need for tempstore to be both secure and temporary.
    Make sure that all arguments passed to constructor are strings or
    unicode strings, except store which needs to be a temp store
    implementing shoplifter.payment.core.ITempStore.
    """
    def __init__(self,
                 transaction_id,
                 number,
                 exp_year=None,
                 exp_month=None,
                 csc=None,
                 cc_type=None):

        self.transaction_id = str(transaction_id)
        self.number = number
        self.exp_month = exp_month
        self.exp_year = exp_year
        self.csc = csc  # Note: Amex is 4 digits.
        self.cc_type = cc_type
        if not self.is_luhn_valid():
            raise self.CardFormatError(
                'Credit card number format fails luhn check')

    @staticmethod
    def get(transaction_id):
        cc = config.temp_store.get(transaction_id)
        if not cc:
            return None
        return CreditCard(
            transaction_id,
            cc['number'],
            cc['exp_month'],
            cc['exp_year'],
            cc['csc'],
            cc['cc_type'],
            )

    def save(self):
        to = config.cc_store_time
        key = self.transaction_id
        cc = {
            'number': self.number,
            'exp_month': self.exp_month,
            'exp_year': self.exp_year,
            'csc': self.csc,
            'cc_type': self.cc_type,
            }
        config.temp_store.store(key, cc, to, encrypted=True)


class DebitCard(PaymentCredential):
    """
    """
    def __init__(self,
                 transaction_id,
                 number):

        self.transaction_id = str(transaction_id)
        self.number = number
        if not self.is_luhn_valid():
            raise self.CardFormatError(
                'Credit card number format fails luhn check')

    @staticmethod
    def get(transaction_id):
        dc = config.temp_store.get(transaction_id)
        if not dc:
            return None
        return DebitCard(
            transaction_id,
            dc['number'],
            )

    def save(self):
        to = config.cc_store_time
        key = self.transaction_id
        dc = {
            'number': self.number,
            }
        config.temp_store.store(key, dc, to, encrypted=True)
