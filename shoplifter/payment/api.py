import decimal
from mongoengine import Q
from shoplifter.payment import plugins


"""
TODO:
Uses another keyword than store? Was suggested 'set' for method name
but will it not override native set object type?
"""

__all__ = ('DummyStore', 'MemcacheStore')


class PayableOrder(object):

    @property
    def payment(self):
        """ This may need to be refactored to some extent... but
        basically, this returns an OrderHelper object that is then
        used to make various queries when given an order instance. """

        # Check if it's bee initialized.
        if not hasattr(self, '_payment_initialized'):
            self._payment = OrderApi(self)
            self._payment_initialized = True

        # Return instance.
        return self._payment

    @property
    def balance(self):
        return self.payment.get_balance()

    @property
    def is_prepared(self):
        return self.payment.is_prepared()


class OrderApi(object):
    """ This is the type of object returned by order.payment. This
    allows to make various queries to the payment system.
    TODO: Change name... not OrderHelper, not querying.py."""

    def __init__(self, order):
        self.order = order

    def get_payments(self, *a, **kw):
        """
        This returns payments matching self.order.id.
        Any parameters passed as keyword arguments or arguments will
        be passed to the mongodb query.
        """
        # TODO: Maybe set a get_payment method for each backend? Or
        # find way to make this more efficient?
        payments = []
        backends = plugins['payment_backends']
        for k in backends.keys():
            payments += list(
                backends[k].payment_class.objects.filter(
                    order_id=self.order.id,
                    backend_key=k,
                    *a,
                    **kw))
        return payments

    def get_payment_sum(self, *a, **kw):
        """
        This is a wrapper for self.get_payments that aggregates the
        sum of 'amount' for the query.
        """
        # TODO: Maybe set a get_payment_sum method for each backend? Or
        # find way to make this more efficient? Howto?
        payment_sum = decimal.Decimal(0)
        backends = plugins['payment_backends']
        for k in backends.keys():
            payments = backends[k].payment_class.objects.filter(
                order_id=self.order.id,
                backend_key=k,
                *a,
                **kw)
            payment_sum += payments.sum('amount')
        return payment_sum

    def get_paid_for_amount(self):
        """
        Returns the sum of all payments that have been successfully processed
        against the payment gateway.
        """
        return self.get_payment_sum(processed=True, success=True)

    def get_prepared_amount(self):
        """
        Returns the sum of all payments that have not yet been
        processed against payment gateway.
        """
        return self.get_payment_sum(processed=False)

    def get_captured_amount(self):
        """
        Returns the cumulated payment amounts for payments that have
        been captured; an authorization needs post-capture, but a
        purchase transaction needs only to be processed to capture the
        funds. You shouldn't to call this other than to debug.
        """
        def reduce_captured_amount(s, payment):
            # TODO: I think this operation should be done with
            # MongoDB instead of python. Think about it.
            if payment.backend.use_pre_auth:
                increment = decimal.Decimal(0) \
                    if not payment.authorization_capture \
                    else payment.authorization_capture.amount
                return s + increment
            else:
                return s + payment.amount
        payments = self.get_payments(processed=True, success=True)
        return reduce(reduce_captured_amount, payments, decimal.Decimal(0))

    def get_prepared_and_processed_payment_amount(self):
        """
        Returns the sum of all payments that have been successfully
        processed, plus the sum of those that have not yet been
        processed, but are prepared.
        """
        return self.get_payment_sum(
            Q(processed=False) | Q(processed=True, success=True))

    def get_balance(self):
        """
        Balance returns the difference between self.order.total and
        the total amount of payments that have been successfully been
        processed.
        """
        return (self.order.total - self.get_paid_for_amount())

    def get_to_prepare_amount(self):
        """
        Returns how much more to prepare payments for. Basically,
        similar to balance, except it also takes into account the
        unprocessed payments.
        """
        return (self.order.total -
                self.get_prepared_and_processed_payment_amount())

    def is_prepared(self):
        """
        Whether or not the payment sum, including prepared and
        sucessfully processed payments is equal to self.order.total.
        """
        return self.get_to_prepare_amount() == decimal.Decimal('0')

    def process_all_payments(self):
        """ TODO: Exception Handling """
        payments = self.get_payments(processed=False)
        for payment in payments:
            payment.process()

    def capture_all_authorizations(self):
        """ TODO: Exception Handling """
        payments = self.get_payments(processed=True)
        for p in payments:
            if p.backend.use_pre_auth:
                if not p.captured:
                    p.capture()
