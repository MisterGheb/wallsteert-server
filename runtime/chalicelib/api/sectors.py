import logging
import requests
import random
import string
import os
import binascii
import leangle
import bcrypt
from chalice import Blueprint, BadRequestError, UnauthorizedError
from sqlalchemy import exc
from marshmallow import exceptions

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
        status="No orders in the system"

    return {'status': status, 'data': SectorsSchema(many=True).dump(sectors)}


@leangle.describe.tags(["Sectors"])
@leangle.describe.parameter(name='body', _in='body', description='Create a new Sector', schema='SectorsSchema')
@leangle.describe.response(200, description='Sector Created', schema='SectorsSchema')
@sectors_routes.route('/', methods=['POST'], cors=True)
def create_sector():
    json_body = sectors_routes.current_request.json_body
    try:
        data_obj = SectorsSchema().load(json_body)
    except TypeError as ex:
        raise BadRequestError(ex)
    except exceptions.ValidationError as ex:
        raise BadRequestError(ex)

    try:
        sector = Sectors.create(**data_obj)
    except exc.IntegrityError as ex:
        raise BadRequestError(ex._message)

    return {'status': 'Success', 'data': SectorsSchema().dump(sector)}


@leangle.describe.tags(["Sectors"])
@leangle.describe.parameter(name='body', _in='body', description='Get Sector', schema='SectorsSchema')
@leangle.describe.response(200, description='Sector Retrieved', schema='SectorsSchema')
@sectors_routes.route('/{sector_id}', methods=['GET'], cors=True)
def get_sector(sector_id):
    sector = Sectors.where(id=sector_id).first()
    status = "Success"
    if(sector == None):
        status = "Sector not Found!"
    return {'status': status, 'data': SectorsSchema().dump(sector)}


@leangle.describe.tags(["Sectors"])
@leangle.describe.parameter(name='body', _in='body', description='Update Sector', schema='SectorsSchema')
@leangle.describe.response(200, description='Sector Updated', schema='SectorsSchema')
@sectors_routes.route('/{sector_id}', methods=['PATCH'], cors=True)
def get_sector(sector_id):
    json_body = sectors_routes.current_request.json_body
    sector = Sectors.where(id=sector_id).first()
    status = "Success"
    if(sector == None):
        status = "Sector not Found!"
        return {'status': status, 'data': SectorsSchema().dump(sector)}

    try:
        data_obj = SectorsSchema().load(json_body)
    except TypeError as ex:
        raise BadRequestError(ex)
    except exceptions.ValidationError as ex:
        raise BadRequestError(ex)
    
    if 'name' in json_body:
        sector.update(name = json_body['name'])
    if 'description' in json_body:
        sector.update(description = json_body['description'])
    return {'status': status, 'data': SectorsSchema().dump(sector)}