__import__('pkg_resources').declare_namespace(__name__)


from shoplifter.payment.models import Authorization, Addressee, \
    AVSData, Payment, AuthorizationCapture
from shoplifter.payment.lib.credentials import CreditCard


class BaseBackend(object):
    """
    This is the base class for Backends. If you write a backend, it
    will be easier if your backend inherits from this class.
    """

    credential_class = CreditCard
    addressee_class = Addressee
    capture_class = AuthorizationCapture
    payment_class = Payment
    avs_class = AVSData
    name = 'basebackend'

    def __init__(self, configuration):
        """ This should initialize the API connections """
        self.use_pre_auth = configuration['use_pre_auth']
        if self.use_pre_auth:
            self.payment_class = Authorization

    def gen_transaction_id(self, order_id, prefixes=[]):
        """This returns an order_id that's built using the prefixes,
        the order_id and the transaction count."""
        prefix = '_'.join(prefixes)
        count = (
            self.payment_class.objects.filter(order_id=order_id).count()
            +
            self.capture_class.objects.filter(order_id=order_id).count())
        trn_id = '%s_%s_%s_%d' % (
            self.name, prefix, str(order_id), count)
        return trn_id

    def purchase(self, payment):
        """ Returns a payment object """
        payment.processed = True
        payment.save()
        return payment

    def authorize(self, auth):
        """ This processed an authorizatons against payment
        gateway. First it needs to set processed to True, so if the
        authorization succeeds, it cannot be processed
        twice, and if it fails, another one needs to be created. """
        auth.processed = True
        auth.save()
        return auth

    def confirm(self, authorization, amount=None):
        if not amount:
            amount = authorization.amount
        auth_capture = self.capture_class(
            transaction_id=self.gen_transaction_id(
                authorization.order_id, prefixes=['confirm', ]),
            order_id=authorization.order_id,
            amount=amount,
            processed=True,
            backend_key=self.name)
        auth_capture.save()
        authorization.captured = True
        authorization.authorization_capture = auth_capture
        authorization.save()
        return auth_capture

    def cancel(self, authorization):
        """ Returns a cancellation object """
        pass

    def refund(self, order):
        """ Returns a refund object """
        pass

    def verify(self, order):
        """
        Returns True or False, depending on backend, this may
        record a 0.01$ transaction. This is used to verify the credit
        card details.
        """
        pass

    def prepare_payment(self, *args, **kwargs):
        """ This prepares the authorization. """
        pass

    class WaitedTooLong(Exception):
        """
        This is raised when a payment credential cannot be found
        in temp storage.
        """
        pass
