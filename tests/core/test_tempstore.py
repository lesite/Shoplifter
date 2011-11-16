from unittest import TestCase
from shoplifter.core.tempstore import MemcacheStore, DummyStore


class TempStoreCase(TestCase):
    def setUp(self):
        self.key = 'testkey123456789'
        self.store_time = 5 * 60,

    def get_mstore(self):
        return MemcacheStore(('127.0.0.1:11211', ), self.key)

    def get_dstore(self):
        return DummyStore(None, self.key)

    def test_memcache_store(self):
        key1 = 'testkey1'
        key2 = 'testkey2'
        expire = 3600
        value = 'testval'
        store = self.get_mstore()
        store.store(key1, value, expire)
        store.store(key2, value, expire, encrypted=True)
        self.assertEquals(store.get(key1), value)
        self.assertEquals(store.get(key2), value)
        self.assertEquals(store.get('nothing'), None)

    def test_dummy_store(self):
        key1 = 'testkey1'
        key2 = 'testkey2'
        expire = 3600
        value = 'testval'
        store = self.get_dstore()
        store.store(key1, value, expire)
        store.store(key2, value, expire, encrypted=True)
        self.assertEquals(store.get(key1), value)
        self.assertEquals(store.get(key2), value)
        self.assertEquals(store.get('nothing'), None)
