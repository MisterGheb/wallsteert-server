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
from ..models.stocks import Stocks
from ..serializers.stocks import StocksSchema
from ..constants import *

stocks_routes = Blueprint('stocks')
logger = logging.getLogger(__name__)