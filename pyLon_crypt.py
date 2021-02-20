import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms
from hashlib import sha256
from base64 import b64decode, b64encode
from random import shuffle, randint


class ChaCha20Crypt:

    """ A much more secure encryption method han the original version."""

    def __init__(self):
        self.__key = b""

    def set_passphrase(self, passphrase: bytes):
        """ setter method for the passphrase """
        if type(passphrase) == bytes:
            self.__key = sha256(passphrase).digest()

    def encrypt_password(self, plain_text: str):
        """ encryption method for passwords """

        nonce = os.urandom(16)  # 16 random bytes
        algorithm = algorithms.ChaCha20(self.__key, nonce)
        cipher = Cipher(algorithm, mode=None)
        encrypt = cipher.encryptor()

        return b64encode(nonce + encrypt.update(plain_text.encode())).decode()

    def decrypt_password(self, cypher_text: str):
        """ decryption method for password """
        decoded = b64decode(cypher_text.encode())
        nonce = decoded[:16]
        algorithm = algorithms.ChaCha20(self.__key, nonce)
        cipher = Cipher(algorithm, mode=None)
        decrypt = cipher.decryptor()
        print(decoded)
        return decrypt.update(decoded[16:]).decode()

    def generate_password(self):  # generates a 16 char pseudo random password
        """ password generator for 16 byte password's """
        keys = [list("abcdefghijklmnopqrstuvwzyz"), list("ABCDEFGHIJKLMNOPQRSTUVWXYZ"),
                list("0123456789"), list(r"`~!@#$%^&*()_+-={}[];:,.<>?")]
        mixture = [5, 5, 3, 3]  # 5 lower, 5 upper, 3 numeric, 3 special
        for c in range(len(keys)):  # randomise the lists above ^
            shuffle(keys[c])
        password = []  # empty list
        for c, i in enumerate(mixture):  # count, item
            for _ in range(i):
                password.append(keys[c][randint(0, len(keys[c]) - 1)])
        shuffle(password)  # should be fairly random at this point
        password = "".join(password)  # concatenate a list to string
        return password, self.encrypt_password(password)  # return both the plain password and the cypher text
