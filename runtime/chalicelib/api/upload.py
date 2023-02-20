import os
import logging
import boto3
import leangle
from chalice import Blueprint, BadRequestError, UnauthorizedError, Response
from chalicelib.authorizer import token_auth


boto3.Session(
    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
    aws_session_token=os.environ.get('AWS_SESSION_TOKEN')
)
bucket_name = 'mina-parallelprocessing-bucket'

upload_routes = Blueprint('upload')
logger = logging.getLogger(__name__)

@leangle.describe.tags(["Upload"])
@leangle.describe.response(201, description='Upload')
@upload_routes.route('/', methods=['POST'], cors=True, authorizer=token_auth)
def upload_file():
    user_id = upload_routes.current_request.context['authorizer']['principalId']
    json_body = upload_routes.current_request.json_body
    file_name = json_body['file_path']
    obj_key = f'upload/{user_id}/{file_name}'
    bucket_name = "mina-parallelprocessing-bucket"
    s3_client = boto3.client('s3')

    try:
        if file_name[-4:] == '.csv':
            print('detected csv')
            url = boto3.client('s3').generate_presigned_post(
                bucket_name, obj_key, Fields={'Content-Type': 'text/csv'}, ExpiresIn=43200
            )
        else:
            url = boto3.client('s3').generate_presigned_post(
                bucket_name, obj_key, ExpiresIn=43200
            )
    except Exception as e:
        print('exception:')
        print(e)
        return Response('', status_code=418)

    return Response({"presigned_url": url}, status_code=201)