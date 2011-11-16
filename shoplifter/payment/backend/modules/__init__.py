__import__('pkg_resources').declare_namespace(__name__)

from shoplifter.payment.backend.modules.dummy import DummyBackend, \
    DummyGiftCardBackend, DummyDebitCardBackend

__all__ = ['DummyBackend', 'DummyGiftCardBackend', 'DummyDebitCardBackend']
