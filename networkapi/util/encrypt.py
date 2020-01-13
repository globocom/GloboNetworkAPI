import hashlib
import logging
from Crypto.Cipher import Blowfish
from Crypto.Random import get_random_bytes

log = logging.getLogger(__name__)


def encrypt_key(text, salt_key):
    try:
        bs = Blowfish.block_size
        extra_bytes = len(text) % bs
        padding_size = bs - extra_bytes
        padding = chr(padding_size) * padding_size
        padded_text = text + padding

        crypt_obj = Blowfish.new(salt_key, Blowfish.MODE_ECB)

        cipher = crypt_obj.encrypt(padded_text)

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


def generate_key():
    try:
        bs = Blowfish.block_size
        return get_random_bytes(bs)

    except Exception as ERROR:
        log.error(ERROR)
