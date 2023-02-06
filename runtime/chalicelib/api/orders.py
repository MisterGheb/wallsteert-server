import logging
import requests
import random
import string
import os
import binascii
import leangle
import bcrypt
from chalice import Blueprint, BadRequestError, UnauthorizedError
from sqlalchemy import desc, asc

from ..authorizer import token_auth
from ..models.orders import Orders
from ..serializers.orders import OrdersSchema
from ..constants import *

orders_routes = Blueprint('orders')
logger = logging.getLogger(__name__)

@leangle.describe.tags(["Orders"])
@leangle.describe.parameter(name='body', _in='body', description='Match orders', schema='OrdersSchema')
@leangle.describe.response(200, description='Matched', schema='OrdersSchema')
@orders_routes.route('/match', methods=['POST'], cors=True)


def match_orders():
    json_body = orders_routes.current_request.json_body
    buy_orders = (Orders.bid_price, Orders.executed_volume).where(type="BUY").order_by(Orders.bid_price.desc())
    sell_orders = (Orders.bid_price, Orders.executed_volume).where(type="SELL").order_by(Orders.bid_price.asc())
    current_price = buy_orders.join(sell_orders).filter(buy_orders.bid_price>=sell_orders.bid_price).all()

    return OrdersSchema().dump(current_price)