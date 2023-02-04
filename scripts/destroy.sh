# Script to destroy the project deployment from the server
# Refer to the documentation for more information - docs/deployment.md


export $(cat .env| xargs)
cd runtime
pip install -r requirements.txt
cd ../infrastructure
pip install -r requirements.txt
cdk destroy --all --require-approval never
