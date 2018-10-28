# -*- coding: utf-8 -*-
from Crypto.Cipher import AES
from binascii import b2a_hex, a2b_hex


class AES_CRY():

    def __init__(self, key):
        self.key = key
        self.mode = AES.MODE_CBC

    def encrypt(self, plaintext):
        """Encrypt a plain text using AES"""
        #encryptor = AES.new(self.key, self.mode, self.key)
        encryptor = AES.new(bytes(str(self.key), encoding="utf8"), self.mode, bytes(str(self.key), encoding="utf8"))
        plaintext = plaintext.encode("utf-8")
        length = 16
        count = len(plaintext)
        add = length - (count % length)
        plaintext = plaintext + (b'\0' * add)
        self.ciphertext = encryptor.encrypt(plaintext)
        # Because output of AES encryption is not necessarily a string of ascii character set, maybe there will be
        # a problem when we output it to the terminal or save, so we unified encrypted string into a hexadecimal string
        return b2a_hex(self.ciphertext).decode("ASCII")

    def decrypt(self, ciphertext):
        """Decrypt a plain text using AES"""
        decryptor = AES.new(self.key, self.mode, self.key)
        plaintext = decryptor.decrypt(a2b_hex(ciphertext))
        return plaintext.rstrip(b'\0').decode("utf-8")

if __name__ == '__main__':
    pc = AES_CRY('keyskeyskeyskeys') # definition of the secret key of the private key
    e = pc.encrypt("1234567890987654321")
    d = pc.decrypt(e)
    print(e)
    print(d)
