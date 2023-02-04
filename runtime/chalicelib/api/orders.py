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
from ..models.orders import Orders
from ..serializers.orders import OrdersSchema
from ..constants import *

orders_routes = Blueprint('orders')
logger = logging.getLogger(__name__)