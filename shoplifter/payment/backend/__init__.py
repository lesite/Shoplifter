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

        capture_class = self.payment_class.get_capture_class()

        prefix = '_'.join(prefixes)
        count = (
            self.payment_class.objects.filter(order_id=order_id).count())

        # There should only be a capture class if this is an Authorization.
        if capture_class:
            count += (
                capture_class.objects.filter(order_id=order_id).count())

        trn_id = '%s_%s_%s_%d' % (
            self.name, prefix, str(order_id), count)
        return trn_id

    def purchase(self, payment):
        raise NotImplementedError

    def authorize(self, authorization):
        raise NotImplementedError

    def confirm(self, authorization, amount=None, force=False):
        raise NotImplementedError

    def cancel(self, authorization):
        raise NotImplementedError

    def refund(self, payment):
        raise NotImplementedError

    class CaptureAlreadyExists(Exception):
        """
        This is raised when an authorizatioin capture already exists
        for a given authorization.
        """

    class WaitedTooLong(Exception):
        """
        This is raised when a payment credential cannot be found
        in temp storage.
        """
        pass
