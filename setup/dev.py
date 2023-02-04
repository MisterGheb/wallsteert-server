import os
import subprocess
from common import parse_env_file, prompt_user, persist_env, update_env_template, EnvStorage
from keys import Keys

root_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..")
os.chdir(root_dir)


def set_up_private_key():
    if os.getenv("RSA_PRIVATE_KEY") is not None and input("use existing RSA key?[y/n]") == "y":
        rsa_private_key = os.getenv("RSA_PRIVATE_KEY")
        with open("keys/private_key.pem", "w+") as file:
            file.write(rsa_private_key)  # type: ignore
    elif os.path.isfile("keys/private_key.pem") and input("use existing RSA key?[y/n]") == "y":
        return
    else:
        print("Enter RSA private-key to decrypt env")
        inp = ''
        rsa_private_key = ''
        with open("keys/private_key.pem", "w+") as file:
            for line in iter(input, inp):
                file.write(line + "\n")
                rsa_private_key += line + "\n"
        if os.getenv("GITPOD_WORKSPACE_URL") is not None:
            os.system(f'gp env RSA_PRIVATE_KEY=\"{rsa_private_key}\"')


def get_user_input(path: str = "env/.env.dev.template"):
    parsed_keys = parse_env_file(path=path)
    if not parsed_keys:
        print(f"{path} is malformed.\nIt is recommended to revert back to an older commit with a valid template file")
        exit(1)
    env_vars = prompt_user(parsed_keys)
    if not env_vars:
        exit(1)
    persist_env(env_vars, EnvStorage.LOCAL_FILE, ".env")


def get_current_git_branch():
    try:
        branch = subprocess.check_output(
            ['git', 'branch', '--show-current']).decode('utf-8').strip()
        return branch
    except:
        return 'main'


set_up_private_key()
with open("keys/private_key.pem", "r") as f:
    rsa_key = f.read()
branch = get_current_git_branch()

if not os.path.isfile(".env") and not os.path.isfile(f"env/.env.{branch}.enc"):
    # first time set up for repo
    print("Creating .env file based on dev template")
    get_user_input()
elif os.path.isfile(f"env/.env.{branch}.enc"):
    try:
        with open('keys/symmetric_keyfile.key.enc', 'rb') as f:
            sym_key = Keys.decrypt_symmetric_key(
                f.read(), bytes(rsa_key, 'utf-8'))
    except Exception as ex:
        print(f"Failed to decrypt key. RSA Private key invalid! {str(ex)}")
        raise ex

    try:
        with open(f"env/.env.{branch}.enc", 'rb') as f:
            env = Keys.decrypt_env(f.read(), sym_key)
        with open('.env', 'wb') as f:
            f.write(env)
    except Exception as ex:
        print(f"Failed to decrypt prod environment. {str(ex)}")
        raise ex
# Load secrets into env
update_env_template()
