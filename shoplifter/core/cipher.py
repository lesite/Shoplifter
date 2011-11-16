from Crypto.Cipher import AES


class Cipher(object):
    """ Configures the encryption system and makes it available for
    the payment module to use. """
    def __init__(self, key):
        self.key = key

    def get_cipher(self):
        """ Returns a Crypto AES Cipher object """
        return AES.new(self.key, AES.MODE_CFB)

    def encrypt(self, data):
        """ Makes call to encrypt data """
        return self.crypt(data, 'encrypt')

    def decrypt(self, data):
        """ Makes call to decrypt data """
        return self.crypt(data, 'decrypt')

    def crypt(self, data, call):
        """ This will encrypt all strings and unicode strings (as
        strings), it accepts str, unicode, dict, list and tuple
        TODO: Return unicode instead of str when passing unicode?
        """
        str_func = getattr(self, '_'.join((call, 'string')))
        func = getattr(self, call)
        if isinstance(data, unicode):
            return str_func(data.encode('utf8'))
        elif isinstance(data, str):
            return str_func(data)
        elif isinstance(data, dict):
            encrypted_data = {}
            for k in data.keys():
                encrypted_data[k] = func(data[k])
            return encrypted_data
        elif isinstance(data, list):
            encrypted_data = []
            for d in data:
                encrypted_data.append(func(d))
            return encrypted_data
        elif isinstance(data, tuple):
            encrypted_data = []
            for d in data:
                encrypted_data.append(func(d))
            return tuple(encrypted_data)
        else:
            return data

    def encrypt_string(self, data):
        """ This is what encrypts strings, called by self.crypt """
        cipher = self.get_cipher()
        return cipher.encrypt(data).encode('hex')

    def decrypt_string(self, data):
        """ This is what decrypts strings, called by self.crypt. This
        always returns unicode data to make it easier on everyone. """
        cipher = self.get_cipher()
        return cipher.decrypt(data.decode('hex')).decode('utf8')
