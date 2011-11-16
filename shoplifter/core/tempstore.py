import memcache
from shoplifter.core.cipher import Cipher


class TempStore(object):
    """
    Base class for Temporary Storage backends. Use as template.
    """

    def __init__(self, key, cipher):
        self.cipher = cipher(key)

    def get(self, key):
        raise NotImplementedError

    def store(self, key, data, time, encrypted=False):
        raise NotImplementedError


dummy_store = {}


class DummyStore(TempStore):
    """
    Simple Dummy Store backend that stores data in the dummy_store
    dictionary.
    """

    def __init__(self, location, key, cipher=Cipher):
        super(DummyStore, self).__init__(key, cipher)

    def get(self, key):
        try:
            data = dummy_store[key]
        except KeyError:
            return None
        if data[1]:
            return self.cipher.decrypt(data[0])
        return data[0]

    def store(self, key, data, time, encrypted=False):
        if encrypted:
            to_store = self.cipher.encrypt(data), encrypted
        else:
            to_store = data, encrypted
        dummy_store[key] = to_store


class MemcacheStore(TempStore):
    """
    This is a working storage backend that works with memcached. This
    is the recommended one to use for storing sensitive data.

    * Make sure that your memcached server is protected by a firewall!
    """

    def __init__(self, location, key, cipher=Cipher):
        super(MemcacheStore, self).__init__(key, cipher)
        self.client = memcache.Client(location)

    def get(self, key):
        data = self.client.get(key)
        if not data:
            return None
        if data[1]:
            return self.cipher.decrypt(data[0])
        return data[0]

    def store(self, key, data, time, encrypted=False):
        if encrypted:
            to_store = self.cipher.encrypt(data), encrypted
        else:
            to_store = data, encrypted
        self.client.set(key, to_store, time)
