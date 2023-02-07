import logging
import requests
import random
import string
import os
import binascii
import leangle
import bcrypt
from chalice import Blueprint, BadRequestError, UnauthorizedError
from sqlalchemy import desc, asc, exc, delete
from marshmallow import exceptions
from datetime import timezone
import datetime

from ..authorizer import token_auth
from ..models.orders import Orders
from ..serializers.orders import OrdersSchema
from ..constants import *

orders_routes = Blueprint('orders')
logger = logging.getLogger(__name__)

@leangle.describe.tags(["Orders"])
@leangle.describe.parameter(name='body', _in='body', description='List All Orders', schema='OrdersSchema')
@leangle.describe.response(200, description='Orders Listed', schema='OrdersSchema')
@orders_routes.route('/', methods=['GET'], cors=True)
def list_orders():
    orders = Orders.all()

    status = "Success"

    if(orders==[]):
        status="No orders in the system"

    return {'status': status, 'data': OrdersSchema(many=True).dump(orders)}



@leangle.describe.tags(["Orders"])
@leangle.describe.parameter(name='body', _in='body', description='Create Order', schema='OrdersSchema')
@leangle.describe.response(200, description='Order Created', schema='OrdersSchema')
@orders_routes.route('/', methods=['POST'], cors=True)
def create_order():
    json_body = orders_routes.current_request.json_body
    try:
        data_obj = OrdersSchema().load(json_body)
    except TypeError as ex:
        raise BadRequestError(ex)
    except exceptions.ValidationError as ex:
        raise BadRequestError(ex)

    if(data_obj['type'] == 'BUY'):
        user = Users.where(id=data_obj['users_id']).first()
        if(user.available_funds < data_obj['bid_price']):
            raise BadRequestError("This user does not have enough available funds to bid on that stock")

    if(data_obj['type'] == 'SELL'):
        holding = Holdings.where(id=data_obj['stocks_id']).first()
        if(holding.volume < data_obj['bid_volume']):
            raise BadRequestError("This user does not have enough of that stock to sell for this bid volume")

    data_obj.update({'status': 'PENDING'})
    data_obj.update({'executed_volume': 0})
    data_obj.update({'created_at': datetime.datetime.now()})

    try:
        order = Orders.create(**data_obj)
    except exc.IntegrityError as ex:
        raise BadRequestError(ex._message)

    return {'status': 'Success', 'data': OrdersSchema().dump(order)}


@leangle.describe.tags(["Orders"])
@leangle.describe.parameter(name='body', _in='body', description='Get Order', schema='OrdersSchema')
@leangle.describe.response(200, description='Order Retrieved', schema='OrdersSchema')
@orders_routes.route('/{orders_id}', methods=['GET'], cors=True)
def get_order(orders_id):
    order = Orders.where(id=orders_id).first()
    status = "Success"

    if(order==None):
        status="Order not found"

    return {'status': status, 'data': OrdersSchema().dump(order)}


@leangle.describe.tags(["Orders"])
@leangle.describe.parameter(name='body', _in='body', description='Delete order', schema='OrdersSchema')
@leangle.describe.response(200, description='Order Deleted', schema='OrdersSchema')
@orders_routes.route('/{orders_id}', methods=['DELETE'], cors=True)
def delete_order(orders_id):
    order = Orders.where(id=orders_id).first()
    status = "Success"

    if(order==None):
        status="Order not found"
        return {'status': status, 'data': OrdersSchema().dump(order)}

    order.delete()

    return {'status': status, 'data': "Order Deleted!"}


@leangle.describe.tags(["Orders"])
@leangle.describe.parameter(name='body', _in='body', description='Match orders', schema='OrdersSchema')
@leangle.describe.response(200, description='Matched', schema='OrdersSchema')
@orders_routes.route('/match', methods=['POST'], cors=True)
def match_orders():
    json_body = orders_routes.current_request.json_body
    buy_orders = Orders.where(type="BUY").order_by(Orders.bid_price.desc())
    #sell_orders = Orders.where(type="SELL").order_by(Orders.bid_price.asc())

    return OrdersSchema().dump(buy_orders)