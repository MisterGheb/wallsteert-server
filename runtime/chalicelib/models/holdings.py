import logging
import requests
import random
import logging
import requests
import random
import string
import os
import binascii
import leangle
import bcrypt
from chalice import Blueprint, BadRequestError, UnauthorizedError, Response
from sqlalchemy import func

from ..authorizer import token_auth
from ..models.holdings import Holdings
from ..serializers.holdings import HoldingsSchema
from ..constants import *
from ..models.stocks import Stocks
from ..models.orders import Orders
holdings_routes = Blueprint('holdings')
logger = logging.getLogger(name)


@leangle.describe.tags(["Holdings"])
@leangle.describe.parameter(name='body', _in='body', description='List Holdings', schema='HoldingsSchema')
@leangle.describe.response(200, description='Holdings Listed', schema='HoldingsSchema')
@holdings_routes.route('/', methods=['GET'], cors=True, authorizer=token_auth)
def list_holdings():
    user_id = holdings_routes.current_request.context['authorizer']['principalId']
    currentStock = 0
    print("function invoked")
    holdings = Holdings.where(users_id=user_id).all()
    if len(holdings) == 0:
        return Response("", status_code=404)
    totalCost = 0
    totalWorth = 0
    portfolio = []
    for holding in holdings:
        print(holding)
        stock = Stocks.where(id=holding.stocks_id).first()
        totalCost += holding.volume * holding.bid_price
        totalWorth += holding.volume *stock.price
        portfolio.append({
                        "id": holding.stocks_id,
                        "name": stock.name,
                        "total_volume": holding.volume,
                        "avg_bid_price": ('%.2f' % holding.bid_price)
                    })
    finalHoldings = {
                "investment": ('%.2f' % totalCost),
                "current_value":  ('%.2f' % totalWorth),
                "stocks_possessed": portfolio
            }
    return finalHoldings