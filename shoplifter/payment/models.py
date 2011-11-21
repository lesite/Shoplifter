from mongoengine import IntField, BooleanField, StringField, \
    EmailField, DateTimeField, EmbeddedDocumentField, \
    ReferenceField, EmbeddedDocument, Document
from shoplifter.payment.lib.fields import MoneyField
from shoplifter.payment import plugins


class Addressee(EmbeddedDocument):
    """
    This is metadata that can optionally be provided to payment
    gateways, for example to define billing and shipping address.
    """
    first_name = StringField(required=True)
    last_name = StringField()
    email = EmailField()
    phone_number = StringField()
    street_number = StringField(required=True)
    street_name = StringField(required=True)
    street_type = StringField()
    unit_number = StringField()
    street_direction = StringField()
    street_line_2 = StringField()
    postal_code = StringField()
    city = StringField(required=True)
    province = StringField(required=True)
    country = StringField(required=True)

    @staticmethod
    def from_order_address(address):
        if not address:
            return None
        return Addressee(
            first_name=address.first_name,
            last_name=address.last_name,
            email=address.email,
            phone_number=address.phone_number,
            street_number=address.street_number,
            street_name=address.street_name,
            street_type=address.street_type,
            street_direction=address.street_direction,
            unit_numer=address.unit_number,
            street_line_2=address.street_line_2,
            postal_code=address.postal_code,
            city=address.city,
            province=address.province,
            country=address.country,
            )

    @staticmethod
    def get_address_pair(order):
        return Addressee.from_order_address(order.billing), \
            Addressee.from_order_address(order.shipping)


class AVSData(EmbeddedDocument):
    """
    This is used to record AVS response data.
    """
    avs_message = StringField()
    avs_result = StringField(max_length=1)
    avs_postal_match = BooleanField()
    avs_address_match = BooleanField()


"""
The following describes the actual data models.
"""


class BaseTransaction(Document):
    """
    Base transaction class that defines the basic behaviour of
    financial transaction objects, including Authorization,
    Authorization Capture, Purchase and Cancellation.

    * id: This is the order_id that's been transmitted
      to the payment gateway.

    * transaction_id: Payment gateways return a transaction ID that
      identifies the transaction in their system. This is where to
      store it.

    * order_id: This should be the order's unique identifier. It is
      used to establish a relationship between orders and
      transactions.

    * processed: Defines whether or not an attempt was made to process
      the transaction against the payment gateway. Anytime that an
      attempt is made to process a transaction, this should be set to
      True, regardless on whether or not it is successful.

    * process_time_stamp: This is the time that the processing attempt
      was attempted.

    * processing_order: This defines the order that transactions
      should be processed. For example, we may want to process
      GiftCard transactions before we process CreditCard ones.

    * backend_key: This is a string that identifies the payment
      backend that set-up this transaction. This is used to select the
      proper payment backend when retrieving the transaction.

    * response_code: This is the transaction response code returned by
      the payment gateway.

    * message: This is the message string that has been returned by
      the payment gateway.
    """
    transaction_id = StringField(unique=True)
    gateway_transaction_id = StringField()
    order_id = StringField(required=True)
    processed = BooleanField()
    processing_order = IntField()
    backend_key = StringField()
    response_code = StringField()
    message = StringField()
    processed_time_stamp = DateTimeField()
    gateway_times_stamp = DateTimeField()

    @property
    def backend(self):
        """ This returns the payment that set up this transaction """
        return plugins['payment_backends'][self.backend_key]

    def process(self):
        raise NotImplementedError


class Payment(BaseTransaction):
    """
    * amount: The money amount requested.

    * billing: This is an Address document. If you want address
      verification to be validated, you need to enter billing data.

    * shipping: You can supply shipping information to some payment
      gateways. If the gateway supports this, this is where you will
      populate the shipping data.

    * success: Whether the transaction was successful or not.

    * csc_result: This is the result for CSC check. This is either one
    of the following:
      0: Fail
      1: Pass
      -1: Not Processed

    * avs_result: This is the address verification result code. This
      may be different for each payment gateway. This should at least
      be recorded and displayed to the site admin when reviewing
      orders.
    TODO: Think of this more?
    """

    amount = MoneyField(required=True)
    billing = EmbeddedDocumentField(Addressee)
    shipping = EmbeddedDocumentField(Addressee)
    success = BooleanField()
    csc_result = IntField()
    avs_result = EmbeddedDocumentField(AVSData)

    @classmethod
    def get_capture_class(cls):
        return None

    def process(self):
        return self.backend.purchase(self)


class AuthorizationCapture(BaseTransaction):
    """
    This is instantiated and saved when capturing an already
    pre-authorized payment.

    * auth_id: Authorization document identifier.
    """
    amount = MoneyField(required=True)
    success = BooleanField()


class Authorization(Payment):
    """
    amount_requested: This is the desired transaction amount.
    amount_approved: This is the amount that's been been approved by
    the payment gateway.

    capture is a reference to the AuthorizationCapture transaction.
    """

    authorization_capture = ReferenceField(AuthorizationCapture)

    @classmethod
    def get_capture_class(cls):
        # Inspect model to find the authorization capture document
        # class.
        return cls._fields['authorization_capture'].document_type_obj

    def create_capture(self, trn_id, amount, backend_name):
        """
        This is called by the BaseBackend as the first steps of
        creating an authorization capture.
        """
        capture = AuthorizationCapture(
            transaction_id=trn_id,
            order_id=self.order_id,
            amount=amount,
            processed=False,
            backend_key=backend_name)
        capture.save()
        self.authorization_capture = capture
        self.save()
        return capture

    def process(self):
        return self.backend.authorize(self)

    def capture(self, force=False):
        return self.backend.confirm(self, self.amount, force)


class Cancellation(BaseTransaction):
    """
    meh
    """
    success = BooleanField()
