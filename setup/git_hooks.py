import os
import shutil

root_dir = os.path.join(os.getcwd())
os.chdir(root_dir)

if os.path.isfile(".git/hooks/pre-commit.sample"):
    os.rename(".git/hooks/pre-commit.sample", ".git/hooks/pre-commit")
if os.path.isfile("post-update.sample"):
    os.rename("post-update.sample", ".git/hooks/post-update")
    os.system("chmod +x post-update")

if not os.path.exists(".git/hooks"):
    os.mkdir(".git/hooks")
shutil.copyfile("setup/hooks/pre-commit", ".git/hooks/pre-commit")
shutil.copyfile("setup/hooks/post-update", ".git/hooks/post-update")
shutil.copyfile("setup/hooks/decrypt_sym_key.py",
                ".git/hooks/decrypt_sym_key.py")
shutil.copyfile("setup/hooks/decrypt_env.py",
                ".git/hooks/decrypt_env.py")
shutil.copyfile("setup/hooks/encrypt_env.py",
                ".git/hooks/encrypt_env.py")
shutil.copyfile("setup/keys.py", ".git/hooks/keys.py")
