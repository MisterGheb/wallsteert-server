import logging
import requests
import random
import string
import os
import binascii
import leangle
import bcrypt
from chalice import Blueprint, BadRequestError, UnauthorizedError

from ..authorizer import token_auth
from ..models.sectors import Sectors
from ..serializers.sectors import SectorsSchema
from ..constants import *

sectors_routes = Blueprint('sectors')
logger = logging.getLogger(__name__)