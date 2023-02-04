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
from ..models.holdings import Holdings
from ..serializers.holdings import HoldingsSchema
from ..constants import *

holdings_routes = Blueprint('holdings')
logger = logging.getLogger(__name__)