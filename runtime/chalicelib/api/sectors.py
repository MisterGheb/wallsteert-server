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

from ..authorizer import token_auth
from ..models.sectors import Sectors
from ..serializers.sectors import SectorsSchema
from ..constants import *

sectors_routes = Blueprint('sectors')
logger = logging.getLogger(__name__)


@leangle.describe.tags(["Sectors"])
@leangle.describe.parameter(name='body', _in='body', description='Create a New Sector', schema='SectorsSchema')
@leangle.describe.response(200, description='Sector Successfully created', schema='SectorsSchema')
@sectors_routes.route('/', methods=['POST'], cors=True)


def sectors():
    json_body = sectors_routes.current_request.json_body
    data_body = SectorsSchema().load(json_body)

    try:
        sectors = Sectors.create(**data_body) 
    except exc.IntegrityError as ex:
        raise BadRequestError(ex._message())


    return SectorsSchema().dump(sectors)