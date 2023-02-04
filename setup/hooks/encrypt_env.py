import sys
from keys import Keys


def main():
    with open('keys/symmetric_keyfile.key', 'rb') as f:
        sym_key = f.read()
    with open(sys.argv[1], 'rb') as f:
        env_enc = Keys.encrypt_env(f.read(), sym_key)
    with open(sys.argv[2], 'wb') as f:
        f.write(env_enc)


if __name__ == "__main__":
    main()
