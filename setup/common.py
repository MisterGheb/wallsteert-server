import os
from typing import List, Dict, Optional
from enum import Enum


class Stage(str, Enum):
    DEV = 'dev'
    PROD = 'prod'


class EnvStorage(str, Enum):
    GITHUB = 'github'
    GITPOD = 'gitpod'
    LOCAL_FILE = 'local_file'

def parse_env_file(path: str) -> Optional[Dict[str, str]]:
    """
    Parses Env file/env template files and return all the keys, as a dictionary
    If the keys have values set in the file, they are returned as doctionary values else empty string
    Additionally, any set values are also set in the environment of the running process 
    """
    env_vars = {}
    try:
        if os.path.exists(path):
            with open(path, "r+") as f:
                content = f.readlines()
            for line in content:
                line = line.strip()
                if not line.startswith("#") and "=" in line:
                    key: str = line.split("=")[0]
                    key.strip()
                    value = line.split("=")[1]
                    value.strip()
                    if value != '':
                        os.environ[key] = value
                    env_vars[key]=value
            return env_vars
        else:
            return None
    except Exception as ex:
        return None

def prompt_user(parsed_vars: Dict[str, str]) -> Dict[str, str]:
    """
    Takes parsed_variables as inputs and prompts user for input values
    If variable already have some set value, those will be prompted as defaults
    Returns env variables as dictionary
    Parameters
    ----------
    parsed_vars : Dict[str, str]

    Returns
    -------
    Dict[str, str]
    
    """
    env_vars = {}
    counter = 0
    keys = list(parsed_vars.keys())
    while counter < len(keys):
        key = keys[counter]
        value = os.getenv(key, None)
        if value is None:
            inp = input(f"{key}: ")
        else:
            if len(value) > 5:
                display_value = value[:5] + '*****'
            else:
                display_value = value
            inp = input(
                f"{key}: [\x1b[;36m{display_value}\x1b[0m]")
            inp.strip()
            if inp == '':
                inp = value
        if inp == '':
            continue
        env_vars[key] = inp
        counter += 1
    return env_vars

def persist_env(env_vars: Dict[str, str], env_storage: EnvStorage, local_file_path: Optional[str] = None):
    """
    Takes env variables as dictionary and persists on one of three possible storages, Gitpod variables, Github secrets, or local file

    Parameters
    ----------
    env_vars : Dict[str, str]
    env_storage : EnvStorage
    local_file_path : Optional[str], optional
        required only if storage is local_file, by default None
    """
    if env_storage == EnvStorage.GITPOD:
            for key, value in env_vars.items():
                os.system(f"gp env {key}=\"{value}\" > /dev/null 2>&1")
    elif env_storage == EnvStorage.GITHUB:
        if os.getenv("GH_TOKEN") == None:
            print("Please set valid value of GH_TOKEN environment variable to run this operation")
        for key, value in env_vars.items():
            os.system(f"gh secret set {key} --body {env_vars[key]} 2&> /dev/null")
    elif env_storage == EnvStorage.LOCAL_FILE and local_file_path is not None:
        parsed_vars = parse_env_file(local_file_path) #check existing files to avoid overwriting
        if parsed_vars is not None:
            env_vars = {**parsed_vars, **env_vars} # merge current and incoming input values, give preference to incoming values in case of a clash
        with open(local_file_path, "w+") as file:
            for key, value in env_vars.items():
                file.write(f"{key}={value}\n")


def update_env_template(env_path: str = ".env", template_path: str = "env/.env.dev.template"):
    """
    Updates a .env template based on actual value in corrosponding .env file

    Parameters
    ----------
    env_path : str, optional
    template_path : str, optional
    """
    env_vars = parse_env_file(path=env_path)
    template_vars = parse_env_file(path=template_path)
    if env_vars is None or template_vars is None:
        return
    with open(template_path, "a+") as file:
        for var in env_vars:
            if var not in template_vars:
                file.write(f"\n{var}=")
