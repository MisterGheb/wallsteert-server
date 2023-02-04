# Script to deploy the project to the server
# Refer to the documentation for more information - docs/deployment.md


cd runtime
pip install -r requirements.txt
cd ../infrastructure
pip install -r requirements.txt
npm install -g aws-cdk
export RUN_MIGRATE=False
cdk deploy --all --require-approval never --outputs-file output.json
cd ..

