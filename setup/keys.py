import base64
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.fernet import Fernet


class Keys():
    @staticmethod
    def utf8(s: bytes):
        return str(s, 'utf-8')

    @staticmethod
    def decrypt_symmetric_key(encrypted_key, private_pem):
        private_key = serialization.load_pem_private_key(
            private_pem,
            password=None,
            backend=default_backend()
        )
        sym_key = private_key.decrypt(
            base64.b64decode(encrypted_key),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return sym_key

    @staticmethod
    def encrypt_env(env, sym_key):
        f = Fernet(sym_key)
        encrypted_env = f.encrypt(env)
        return encrypted_env

    @staticmethod
    def decrypt_env(encrypted_env, sym_key):
        f = Fernet(sym_key)
        decrypted_env = f.decrypt(encrypted_env)
        return decrypted_env
