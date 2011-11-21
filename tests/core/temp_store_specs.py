# Monkeypatching memcache client to use mockcache instead.
import memcache
import mockcache
memcache.Client = mockcache.Client

from shoplifter.core.tempstore import (
    TempStore, MemcacheStore, DummyStore)
from shoplifter.core.util import Cipher
from unittest import TestCase
from nose.tools import assert_equals, assert_raises


class TempStoreSpecs(TestCase):
    def setUp(self):
        self.key = 'testkey123456789'
        self.store_time = 5 * 60,

    def get_mstore(self):
        return MemcacheStore(('127.0.0.1:11211', ), self.key)

    def get_dstore(self):
        return DummyStore(None, self.key)

    def it_fails_when_badly_implemented(self):

        class SampleStore(TempStore):
            pass

        sample = SampleStore('1234567890123456', Cipher)
        assert_raises(NotImplementedError, sample.get, *(None, ))
        assert_raises(NotImplementedError, sample.store, *(None, None, None, None))
        assert_raises(NotImplementedError, sample.delete, *(None, ))

    def test_memcache_store(self):
        key1 = 'testkey1'
        key2 = 'testkey2'
        expire = 3600
        value = 'testval'
        store = self.get_mstore()
        store.store(key1, value, expire)
        store.store(key2, value, expire, encrypted=True)
        assert_equals(store.get(key1), value)
        assert_equals(store.get(key2), value)
        assert_equals(store.get('nothing'), None)
        store.delete(key1)
        assert_equals(store.get(key1), None)

    def test_dummy_store(self):
        key1 = 'testkey1'
        key2 = 'testkey2'
        expire = 3600
        value = 'testval'
        store = self.get_dstore()
        store.store(key1, value, expire)
        store.store(key2, value, expire, encrypted=True)
        assert_equals(store.get(key1), value)
        assert_equals(store.get(key2), value)
        assert_equals(store.get('nothing'), None)
        store.delete(key1)
        assert_equals(store.get(key1), None)
