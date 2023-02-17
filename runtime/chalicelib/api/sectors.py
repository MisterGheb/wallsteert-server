import logging
import requests
import random
import string
import os
import binascii
import leangle
import bcrypt
from chalice import Blueprint, BadRequestError, UnauthorizedError, Response
from sqlalchemy import exc
from marshmallow import exceptions
from ..models.users import Users as User

from ..authorizer import token_auth
from ..models.sectors import Sectors
from ..serializers.sectors import SectorsSchema
from ..constants import *

sectors_routes = Blueprint('sectors')
logger = logging.getLogger(__name__)

@leangle.describe.tags(["Sectors"])
@leangle.describe.parameter(name='body', _in='body', description='List all sectors', schema='SectorsSchema')
@leangle.describe.response(200, description='Sectors Listed', schema='SectorsSchema')
@sectors_routes.route('/', methods=['GET'], cors=True)
def list_sectors():
    sectors = Sectors.all()
    status = "Success"
    if(sectors==[]):
        Response("", status_code=404)

    return SectorsSchema(many=True).dump(sectors)


@leangle.describe.tags(["Sectors"])
@leangle.describe.parameter(name='body', _in='body', description='Create a new Sector', schema='SectorsSchema')
@leangle.describe.response(200, description='Sector Created', schema='SectorsSchema')
@sectors_routes.route('/', methods=['POST'], cors=True, authorizer=token_auth)
def create_sector():
    user_id = sectors_routes.current_request.context['authorizer']['principalId']
    user = User.find_or_fail(user_id)
    json_body = sectors_routes.current_request.json_body
    try:
        data_obj = SectorsSchema().load(json_body)
    except TypeError as ex:
        return Response("", status_code=400)
    except exceptions.ValidationError as ex:
        return Response("", status_code=400)

    print(f"this is the create sector{json_body}")
    if json_body.get('name') is None:
        return Response("", status_code=400)
    try:
        sector = Sectors.create(**data_obj)
    except exc.IntegrityError as ex:
        return Response("", status_code=400)

    return Response(SectorsSchema().dump(sector), status_code=200)


@leangle.describe.tags(["Sectors"])
@leangle.describe.parameter(name='body', _in='body', description='Get Sector', schema='SectorsSchema')
@leangle.describe.response(200, description='Sector Retrieved', schema='SectorsSchema')
@sectors_routes.route('/{sector_id}', methods=['GET'], cors=True)
def get_sector(sector_id):
    sector = Sectors.where(id=sector_id).first()
    status = "Success"
    if(sector == None):
        return Response("", status_code=404)
    return SectorsSchema().dump(sector)


@leangle.describe.tags(["Sectors"])
@leangle.describe.parameter(name='body', _in='body', description='Update Sector', schema='SectorsSchema')
@leangle.describe.response(200, description='Sector Updated', schema='SectorsSchema')
@sectors_routes.route('/{sector_id}', methods=['PATCH'], cors=True, authorizer=token_auth)
def get_sector(sector_id):
    user_id = sectors_routes.current_request.context['authorizer']['principalId']
    user = User.find_or_fail(user_id)
    json_body = sectors_routes.current_request.json_body
    sector = Sectors.where(id=sector_id).first()
    status = "Success"
    if(sector == None):
        Response("", status_code=404)
    
    if 'name' in json_body:
        sector.update(name = json_body['name'])
    if 'description' in json_body:
        sector.update(description = json_body['description'])
    return Response(SectorsSchema().dump(sector), status_code=200)