import os
import sys

from keys import Keys


encrypted_file_path = sys.argv[1]

if not os.path.isfile("keys/private_key.pem"):
    rsa_key = os.getenv("RSA_PRIVATE_KEY")
    if rsa_key is None:
        print("RSA Private Key not found.")
        exit(1)
else:
    with open("keys/private_key.pem", "r") as f:
        rsa_key = f.read()


if not os.path.isfile(encrypted_file_path):
    print("encrypted secrets not Found, cannot run without secrets")
    exit(1)

try:
    with open('keys/symmetric_keyfile.key.enc', 'rb') as f:
        sym_key = Keys.decrypt_symmetric_key(f.read(), bytes(rsa_key, 'utf-8'))
except Exception as ex:
    print(f"Failed to decrypt key. RSA Private key invalid! {str(ex)}")
    raise ex

try:
    with open(encrypted_file_path, 'rb') as f:
        env = Keys.decrypt_env(f.read(), sym_key)
    with open('.env', 'wb') as f:
        f.write(env)

except Exception as ex:
    print(f"Failed to decrypt prod environment. {str(ex)}")
    raise ex
