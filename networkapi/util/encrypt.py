import hashlib
import logging
from Crypto.Cipher import Blowfish

log = logging.getLogger(__name__)

INPUT_SIZE = 8


def encrypt_key(key, salt_key):
    try:
        new_str = key
        pad_chars = INPUT_SIZE - (len(key) % INPUT_SIZE)

        if pad_chars != 0:
            for x in range(pad_chars):
                new_str += " "

        crypt_obj = Blowfish.new(salt_key, Blowfish.MODE_ECB)

        cipher = crypt_obj.encrypt(new_str)

        return cipher
    except Exception as ERROR:
        log.error(ERROR)


def decrypt_key(cipher, salt_key):
    try:
        crypt_obj = Blowfish.new(salt_key, Blowfish.MODE_ECB)
        decrypted_key = crypt_obj.decrypt(cipher)

        padding_size = ord(decrypted_key[-1])

        text = decrypted_key[:-padding_size]

        log.debug("Decrypt key was made successfully")
        return str(text)

    except Exception as ERROR:
        log.error(ERROR)


def generate_key(password, salt, iterations):
    assert iterations > 0

    key = password + salt

    for i in range(iterations):
        key = hashlib.sha256(key).digest()

    return key
