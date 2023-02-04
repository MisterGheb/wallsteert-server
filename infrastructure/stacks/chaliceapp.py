import os

from aws_cdk import (
    aws_dynamodb as dynamodb,
    aws_s3 as s3,
    core as cdk,
    aws_certificatemanager as acm,
    aws_route53 as route53,
    aws_ec2 as ec2
)
from chalice.cdk import Chalice
from dotenv import load_dotenv, dotenv_values

load_dotenv()
config = dotenv_values()
reserved_env_var_keys = ['AWS_REGION', 'AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'AWS_DEFAULT_REGION']
for reserved_env_var_key in reserved_env_var_keys:
    if reserved_env_var_key in config:
        del config[reserved_env_var_key]


RUNTIME_SOURCE_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), os.pardir, 'runtime')


class ChaliceApp(cdk.Stack):

    def __init__(self, scope, id, **kwargs):
        super().__init__(scope, id, **kwargs)

        # # Domain and Hosted Zone
        # self.domain = "process-bp-api.tu2k22.devfactory.com"
        # self.hosted_zone = route53.HostedZone.from_lookup(self, 'TUDevFactoryHostedZone', domain_name="tu2k22.devfactory.com")

        # # ACM Certificate
        # certificate_arn = os.getenv("ACM_CERTIFICATE_ARN")
        # self.certificate = acm.Certificate.from_certificate_arn(
        #    self, certificate_arn=certificate_arn, id="ssl-certificate")

        # VPC
        
        vpc = ec2.Vpc.from_lookup(self, "vpc", vpc_id=os.getenv("VPC_ID"))
        security_group = ec2.SecurityGroup(self, id='security-group', allow_all_outbound=True, vpc=vpc)
        security_group.add_ingress_rule(ec2.Peer.any_ipv4(),
                                ec2.Port.tcp(80), "Public HTTP Traffic")
        subnet_ids = list(map(lambda x: x.subnet_id, vpc.private_subnets))
        

        # Chalice
        self.chalice = Chalice(
            self, 'ChaliceApp', source_dir=RUNTIME_SOURCE_DIR,
            stage_config={
                "api_gateway_stage": "api",
                "autogen_policy": True,
                
                "subnet_ids": subnet_ids,
                "security_group_ids": [security_group.security_group_id],
                
                # "api_gateway_custom_domain": {
                #     "domain_name": self.domain,
                #     "certificate_arn": certificate_arn
                # },
               "tags": {
                    "AD": "minaghebrial",
                    "Project": "TU Feb 2023 <Mina>",
                    "Email": "mina.ghebrial@trilogy.com",
                    # "Quarter": "", # add your quater here
                    "Owner": "Mina Ghebrial",
                    "Deletion-advice": "Do not delete",
                    "Template": "Process BP Chalice Template"
                },
                "environment_variables": config
            }
        )

        # self.custom_domain = self.chalice.get_resource("ApiGatewayCustomDomain")
        # self.a_record = route53.CfnRecordSet(
        #     self,
        #     "api-subdomain",
        #     hosted_zone_id=self.hosted_zone.hosted_zone_id,
        #     name=self.domain,
        #     type="A",
        #     alias_target=route53.CfnRecordSet.AliasTargetProperty(
        #         dns_name=self.custom_domain.get_att("DistributionDomainName").to_string(),
        #         hosted_zone_id=self.custom_domain.get_att(
        #             "DistributionHostedZoneId"
        #         ).to_string(),
        #         evaluate_target_health=False,
        #     ),
        # )
        # self.add_tags()
