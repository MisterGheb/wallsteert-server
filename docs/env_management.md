# Managing Secrets & Environments
* After the first time setup of environment variables a `.env` file is generated with the provided values.
* After making a commit, the environment variables and secrets in this `.env` file are encrypted and stored in git. The next time the repo is opened in devspaces, the `.env` will automatically be populated
* Additionally, any time the environment variables have to be changed, users should simply make a change to the `.env` file and make a commit. Git will prompt the users to confirm they want to persist the changes they've made.
* Beyond editing the respective `.env` files, users need not do anything else for managing secrets & environment variables

## Limitations
Since the environment variables are being tracked directly inside git, it places certain constraints on how users can use and update these env. vars

They are as follows
1. Changes made to a `.env` file on a branch other than main will not be persisted in git and will be preserved only in the respective local environment. Users will be warned regarding this if any changes are detected on commits in non-default branches
2. Users are not allow to commit on main locally unless they're up-to-date with the remote. If they try to, git will block the commit and provide the user with the required instructions needed to become up-to-date with remote without loosing their changes

