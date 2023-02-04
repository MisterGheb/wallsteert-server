#!/usr/bin/env python3
import os
import re

from aws_cdk import core as cdk
from stacks.chaliceapp import ChaliceApp

if not os.getenv("ENVIRONMENT_NAME") or os.getenv("ENVIRONMENT_NAME") == 'main':
    ENVIRONMENT_NAME = 'PROD'
else:
    ENVIRONMENT_NAME = os.getenv("ENVIRONMENT_NAME").upper()

app = cdk.App()
ChaliceApp(
    app,
    '-'.join([w for w in re.split(r"[^a-zA-Z0-9]",
             f'tu_feb_2023__mina-TU Wallstreet Server Mina-{ENVIRONMENT_NAME}') if w]).lower(),
    env=cdk.Environment(account=os.getenv(
        'CDK_DEFAULT_ACCOUNT'), region='us-east-1'),
    description="This is a stack created from Process BP Chalice Template"
)

app.synth()
