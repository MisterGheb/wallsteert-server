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
from chalice import Blueprint, BadRequestError, UnauthorizedError
from sqlalchemy import func

from ..authorizer import token_auth
from ..models.holdings import Holdings
from ..serializers.holdings import HoldingsSchema
from ..constants import *
from ..models.stocks import Stocks
from ..models.orders import Orders
holdings_routes = Blueprint('holdings')
logger = logging.getLogger(__name__)


@leangle.describe.tags(["Holdings"])
@leangle.describe.parameter(name='body', _in='body', description='List Holdings', schema='HoldingsSchema')
@leangle.describe.response(200, description='Holdings Listed', schema='HoldingsSchema')
@holdings_routes.route('/', methods=['GET'], cors=True, authorizer=token_auth)
def list_holdings():
    user_id = holdings_routes.current_request.context['authorizer']['principalId']
    currentStock = 0
    json_body = holdings_routes.current_request.json_body
    print(json_body)
    holdings = Holdings.where(users_id=user_id).all()
    returnHoldings = []
    sorted_list = sorted(holdings, key=lambda x: x.stocks_id)
    for holding in sorted_list:
        stock = Stocks.where(id=holding.stocks_id).all()[0]
        order = Orders.where(users_id=holding.users_id, stocks_id=stock.id)
        sumBidPrice = 0
        sumVolume = 0
        for o in order:
            sumBidPrice += o.bid_price*o.executed_volume
            sumVolume += o.executed_volume
        avg_bid_price = sumBidPrice/sumVolume
        if currentStock == stock.id:
            pass
        else: 
            currentStock = stock.id
            returnHoldings.append({
                "current_value": round(stock.price , 2),
                "stocks_possessed": [
                    {
                        "id": holding.stocks_id,
                        "name": stock.name,
                        "total_volume": sumVolume,
                        "avg_bid_price": round(avg_bid_price, 2)
                    }
                ]
            })
    totalStocks = 0
    totalCost = 0
    totalWorth = 0
    portfolio = []
    for element in returnHoldings:
        print(element)
        totalCost += element["stocks_possessed"][0]["total_volume"] * element["stocks_possessed"][0]["avg_bid_price"]
        totalWorth += element["stocks_possessed"][0]["total_volume"] * element["current_value"]
        portfolio.append(element["stocks_possessed"])
    finalHoldings = {
                "investment": round(totalCost, 2),
                "current_value": round(totalWorth, 2),
                "stocks_possessed": portfolio
            }
    return finalHoldings