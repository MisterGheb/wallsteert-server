from keys import Keys


def main():
    with open("keys/private_key.pem", "r") as f:
        rsa_key = f.read()
    with open('keys/symmetric_keyfile.key.enc', 'rb') as f:
        sym_key = Keys.decrypt_symmetric_key(f.read(), bytes(rsa_key, 'utf-8'))
    with open('keys/symmetric_keyfile.key', 'wb') as f:
        f.write(sym_key)


if __name__ == "__main__":
    main()
