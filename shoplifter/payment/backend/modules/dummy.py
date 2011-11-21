from shoplifter.payment.lib.credentials import GiftCard, DebitCard
from shoplifter.payment.backend import BaseBackend
from shoplifter.payment.backend.modules.dummy_controllers import (
    enable_controllers, DummyDebitLookup)


class TransactionTypeNotSupported(Exception):
    pass


class DummyBackend(BaseBackend):
    name = 'dummypayment'

    def prepare_payment(self, order, amount, cc_num, exp_year, exp_mo,
                              csc=None, processing_order=1):
        # TODO!! Need to figure out exception handling.
        # Do we want the backend to take care of removing this if it
        # fails? How do we deal with this? Create a faild payment?

        transaction_id = self.gen_transaction_id(order.id)
        billing, shipping = self.addressee_class.get_address_pair(order)
        data = {
            'transaction_id': transaction_id,
            'order_id': order.id,
            'amount': amount,
            'processed': False,
            'processing_order': processing_order,
            'backend_key': self.name,
            'billing': billing,
            'shipping': shipping,
            }
        cc = self.credential_class(
            transaction_id, cc_num, exp_year, exp_mo, csc)
        cc.save()
        payment = self.payment_class(**data)
        payment.save()
        return payment

    def purchase(self, payment):
        payment.processed = True

        # Get gateway order id to retrive CC.
        transaction_id = payment.transaction_id.encode('utf8')

        # Get credit card from encrypted temp storage.
        cc = self.credential_class.get(transaction_id)

        # Fails if not present.
        if not cc:
            raise self.WaitedTooLong()

        # Payment code to contact payment gateway would go
        # here..

        # Now save avs data.
        avs_res = self.avs_class(
            avs_message='Postal code and verything matches!',
            avs_result='F',
            avs_postal_match=True,
            avs_address_match=True,
            )
        payment.avs_result = avs_res

        # Set csc result (which is usually an integer coming from
        # payment gateway
        payment.csc_result = 1

        # Auth is successful!
        payment.success = True

        # Save in DB.
        payment.save()

        return payment.success

    def authorize(self, authorization):
        authorization.processed = True

        transaction_id = authorization.transaction_id.encode('utf8')

        # Get credit card from encrypted temp storage.
        cc = self.credential_class.get(transaction_id)

        # Fails if not present.
        if not cc:
            raise self.WaitedTooLong()

        # Authorization code to contact payment gateway would go
        # here..

        # Now save avs data.
        avs_res = self.avs_class(
            avs_message='Postal code and verything matches!',
            avs_result='F',
            avs_postal_match=True,
            avs_address_match=True,
            )
        authorization.avs_result = avs_res

        # Set csc result (which is usually an integer coming from
        # payment gateway
        authorization.csc_result = 1

        # Auth is successful!
        authorization.success = True

        # Save in DB.
        authorization.save()

        return authorization.success

    def confirm(self, authorization, amount=None, force=False):
        """
        authorization : The authorization object to confirm.
        amount : The amount to confirm (most likely the pre-auth
            amount)
        force : if a capture exists but is not yet processed, this
            could mean that something went wrong or that another
            instance is already trying to capture. Force will ignore
            this fact and attempt to capture anyways.
        """
        # Prepare data.
        if not amount:
            amount = authorization.amount

        trn_id = self.gen_transaction_id(
                authorization.order_id)

        # Perform a few checks:
        capture = authorization.authorization_capture
        if not capture:
            capture = authorization.create_capture(trn_id, amount, self.name)
        elif capture and ((not capture.processed and not force)
                          or capture.processed):
            raise self.CaptureAlreadyExists

        # Create capture

        capture.processed = True
        capture.success = True
        capture.save()
        return capture


class DummyDebitCardBackend(BaseBackend):
    name = 'dummydebit'
    credential_class = DebitCard

    def __init__(self, *a, **kw):
        super(DummyDebitCardBackend, self).__init__(*a, **kw)
        # Provide some controllers for payment systems that require
        # post-back from third party site.
        # TODO: Make this work.
        if enable_controllers:
            self.controller = DummyDebitLookup(self)

    def prepare_payment(self, order, amount, dc_num,
                              processing_order=0):
        """
        Note that processing_order is set to 0 here, because the
        system assumes that gift card transactions should be processed
        before credit card ones.
        """
        transaction_id = self.gen_transaction_id(order.id)
        billing, shipping = self.addressee_class.get_address_pair(order)
        data = {
            'transaction_id': transaction_id,
            'order_id': order.id,
            'amount': amount,
            'processed': False,
            'processing_order': processing_order,
            'backend_key': self.name,
            'billing': billing,
            'shipping': shipping,
            }
        dc = self.credential_class(
            transaction_id, dc_num)
        dc.save()
        payment = self.payment_class(**data)
        payment.save()
        return payment

    def purchase(self, payment):
        payment.processed = True

        transaction_id = payment.transaction_id.encode('utf8')
        dc = self.credential_class.get(transaction_id)
        if not dc:
            raise self.WaitedTooLong()
        payment.success = True
        payment.save()
        return True

    def authorize(self, authorization):
        raise TransactionTypeNotSupported


class DummyGiftCardBackend(BaseBackend):
    name = 'dummygiftcard'
    credential_class = GiftCard

    def prepare_payment(self, order, amount, gc_num,
                              processing_order=0):
        """
        Note that processing_order is set to 0 here, because the
        system assumes that gift card transactions should be processed
        before credit card ones.
        """
        transaction_id = self.gen_transaction_id(order.id)
        billing, shipping = self.addressee_class.get_address_pair(order)
        data = {
            'transaction_id': transaction_id,
            'order_id': order.id,
            'amount': amount,
            'processed': False,
            'processing_order': processing_order,
            'backend_key': self.name,
            'billing': billing,
            'shipping': shipping,
            }
        gc = self.credential_class(
            transaction_id, gc_num)
        gc.save()
        payment = self.payment_class(**data)
        payment.save()
        return payment

    def purchase(self, payment):
        payment.processed = True

        transaction_id = payment.transaction_id.encode('utf8')
        gc = self.credential_class.get(transaction_id)
        if not gc:
            raise self.WaitedTooLong()
        payment.success = True
        payment.save()
        return True

    def authorize(self, authorization):
        authorization.processed = True

        transaction_id = authorization.transaction_id.encode('utf8')
        gc = self.credential_class.get(transaction_id)
        if not gc:
            raise self.WaitedTooLong()
        authorization.success = True
        authorization.save()
        return True

    def confirm(self, authorization, amount=None, force=False):
        """
        authorization : The authorization object to confirm.
        amount : The amount to confirm (most likely the pre-auth
            amount)
        force : if a capture exists but is not yet processed, this
            could mean that something went wrong or that another
            instance is already trying to capture. Force will ignore
            this fact and attempt to capture anyways.
        """
        # Prepare data.
        if not amount:
            amount = authorization.amount

        trn_id = self.gen_transaction_id(
                authorization.order_id)

        # Perform a few checks:
        capture = authorization.authorization_capture
        if not capture:
            capture = authorization.create_capture(trn_id, amount, self.name)
        elif capture and ((not capture.processed and not force)
                          or capture.processed):
            raise self.CaptureAlreadyExists

        # Create capture

        capture.processed = True
        capture.success = True
        capture.save()
        return capture
