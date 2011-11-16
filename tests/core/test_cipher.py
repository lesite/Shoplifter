# -*- coding: utf-8 -*-

from unittest import TestCase
from shoplifter.core.cipher import Cipher


class CipherCase(TestCase):
    def setUp(self):
        self.cipher = Cipher('testkey123456789')

    def test_cipher_string(self):
        original = 'derp herp'
        expected_encrypted = 'a89d1d6f224e8f2a3c'
        encrypted = self.cipher.encrypt(original)
        decrypted = self.cipher.decrypt(encrypted)
        self.assertEquals(encrypted, expected_encrypted)
        self.assertEquals(original, decrypted)

    def test_cipher_unicode(self):
        original = u'Mêlé comme ça.'
        expected_encrypted = '81df5bd6334f72c3767487febb58c4c456'
        encrypted = self.cipher.encrypt(original)
        decrypted = self.cipher.decrypt(encrypted)
        self.assertEquals(encrypted, expected_encrypted)
        self.assertEquals(original, decrypted)

    def test_cipher_dict(self):
        original = {1: 'derp herp'}
        expected_encrypted = {1: 'a89d1d6f224e8f2a3c'}
        encrypted = self.cipher.encrypt(original)
        decrypted = self.cipher.decrypt(encrypted)
        self.assertEquals(encrypted, expected_encrypted)
        self.assertEquals(original, decrypted)

    def test_cipher_list(self):
        original = ['derp herp', ]
        expected_encrypted = ['a89d1d6f224e8f2a3c', ]
        encrypted = self.cipher.encrypt(original)
        decrypted = self.cipher.decrypt(encrypted)
        self.assertEquals(encrypted, expected_encrypted)
        self.assertEquals(list(original), decrypted)

    def test_cipher_tuple(self):
        original = ('derp herp', )
        expected_encrypted = ('a89d1d6f224e8f2a3c', )
        encrypted = self.cipher.encrypt(original)
        decrypted = self.cipher.decrypt(encrypted)
        self.assertEquals(encrypted, expected_encrypted)
        self.assertEquals(original, decrypted)

    def test_cipher_tuple_with_int(self):
        original = ('derp herp', 2)
        expected_encrypted = ('a89d1d6f224e8f2a3c', 2)
        encrypted = self.cipher.encrypt(original)
        decrypted = self.cipher.decrypt(encrypted)
        self.assertEquals(encrypted, expected_encrypted)
        self.assertEquals(original, decrypted)
