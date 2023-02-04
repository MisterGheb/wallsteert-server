import os
import logging
import requests
import json

import aws_cdk.cx_api as cx_api
import requests

logger = logging.getLogger(__name__)

try:
    RSA_PRIVATE_KEY = os.getenv("RSA_PRIVATE_KEY")
    ENVIRONMENT_NAME = os.getenv("ENVIRONMENT_NAME")
    REPOSITORY_NAME = os.getenv("REPOSITORY_NAME")
except Exception as e:
    logger.error("Not able to get env variables")
    raise e


resources = []
try:
    cloud_assembly = cx_api.CloudAssembly("infrastructure/cdk.out")
    for stack in cloud_assembly.stacks:
        resource = stack.template["Resources"]
        resource["stack_name"] = stack.stack_name
        resources.append(resource)
except Exception as e:
    logger.error("Cannot read resources from cdk.out")
    raise e


add_resources_api = "https://process-bp-api.tu2k22.devfactory.com/resources/add_aws_resources/"

output = {}
try:
    with open('infrastructure/output.json') as f:
        output = json.load(f)
except Exception as e:
    logger.error("Not able to find output.json")
    raise e


payload = {
    "output":  json.dumps(output),
    "branch": ENVIRONMENT_NAME,
    "resources": json.dumps(resources),
    "repository": REPOSITORY_NAME,
    "private_rsa_key": RSA_PRIVATE_KEY
}

try:
    r = requests.post(
        add_resources_api,
        headers={"content-type": "application/json"},
        data=json.dumps(payload))
except Exception as e:
    logger.error("Not able to send request")
    raise e
