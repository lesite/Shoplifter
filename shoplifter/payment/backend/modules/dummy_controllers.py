try:
    from web.core import RESTMethod, Controller
    from web.http import HTTPNotFound
except ImportError:
    enable_controllers = False
    DummyDebitLookup = None
else:
    enable_controllers = True

    class DummyDebitController(RESTMethod):
        def __init__(self, payment, backend, *a, **kw):
            super(DummyDebitController, *a, **kw)
            self.backend = backend
            self.payment = payment

        def post(self, gateway_transaction_id):
            self.backend.prepare_payment(self.transaction)

    class DummyDebitLookup(Controller):
        def __init__(self, backend, *a, **kw):
            self.backend = backend
            super(DummyDebitLookup, self).__init__(*a, **kw)

        def lookup(self, trn_id, *args):
            try:
                transaction = self.backend.payment_class.objects.get(
                    transaction_id=trn_id)
                return DummyDebitController(transaction, self.backend), args
            except self.backend.payment_class.DoesNotExist:
                raise HTTPNotFound
