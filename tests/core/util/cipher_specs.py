# -*- coding: utf-8 -*-

from nose.tools import assert_equals
from shoplifter.core.util import Cipher


class CipherSpecs(object):
    def setup(self):
        self.cipher = Cipher('testkey123456789')

    def can_encrypt_a_string(self):
        original = 'derp herp'
        expected_encrypted = 'a89d1d6f224e8f2a3c'
        encrypted = self.cipher.encrypt(original)
        decrypted = self.cipher.decrypt(encrypted)
        assert_equals(encrypted, expected_encrypted)
        assert_equals(original, decrypted)

    def can_encrypt_a_unicode_string(self):
        original = u'Mêlé comme ça.'
        expected_encrypted = '81df5bd6334f72c3767487febb58c4c456'
        encrypted = self.cipher.encrypt(original)
        decrypted = self.cipher.decrypt(encrypted)
        assert_equals(encrypted, expected_encrypted)
        assert_equals(original, decrypted)

    def can_encrypt_a_dictionary(self):
        original = {1: 'derp herp'}
        expected_encrypted = {1: 'a89d1d6f224e8f2a3c'}
        encrypted = self.cipher.encrypt(original)
        decrypted = self.cipher.decrypt(encrypted)
        assert_equals(encrypted, expected_encrypted)
        assert_equals(original, decrypted)

    def can_encrypt_a_list(self):
        original = ['derp herp', ]
        expected_encrypted = ['a89d1d6f224e8f2a3c', ]
        encrypted = self.cipher.encrypt(original)
        decrypted = self.cipher.decrypt(encrypted)
        assert_equals(encrypted, expected_encrypted)
        assert_equals(list(original), decrypted)

    def can_encrypt_tuple(self):
        original = ('derp herp', )
        expected_encrypted = ('a89d1d6f224e8f2a3c', )
        encrypted = self.cipher.encrypt(original)
        decrypted = self.cipher.decrypt(encrypted)
        assert_equals(encrypted, expected_encrypted)
        assert_equals(original, decrypted)

    def can_encrypt_a_tuple_containing_integer(self):
        original = ('derp herp', 2)
        expected_encrypted = ('a89d1d6f224e8f2a3c', 2)
        encrypted = self.cipher.encrypt(original)
        decrypted = self.cipher.decrypt(encrypted)
        assert_equals(encrypted, expected_encrypted)
        assert_equals(original, decrypted)
