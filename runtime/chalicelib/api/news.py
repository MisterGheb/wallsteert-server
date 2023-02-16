import requests
import boto3
from requests_aws4auth import AWS4Auth
import logging
import leangle
from chalice import Blueprint, Response

host = "https://vpc-ti-shared-e2wxgh4hpjqlvfgbqe472c4maa.us-east-1.es.amazonaws.com/"
region = 'us-east-1'
service = 'es'
credentials = boto3.Session().get_credentials()
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service)
path = 'tu-fe1e0e/_search' # the OpenSearch API endpoint
url = host + path

news_routes = Blueprint(__name__)
logger = logging.getLogger(__name__)

@leangle.describe.tags(["News"])
@leangle.describe.parameter(name='q', _in='body', description='search term to fetch news')
@leangle.describe.response(200, description='News')
@news_routes.route('/', methods=['GET'], cors=True)
def list_news():
    if not news_routes.current_request.query_params:
        raise BadRequestError("Missing required parameter: 'q'")
    company_name = news_routes.current_request.query_params.get('q', None)
    if not company_name:
        raise BadRequestError("Missing required parameter: 'q'")

    payload = {
        "query": {
            "multi_match": {
                "query": company_name
            }
        }
    }
    r = requests.get(url, auth=awsauth, json=payload)
    data = r.json()
    return Response(data, status_code=200)