import logging
import leangle
from chalice import Blueprint, Response, BadRequestError
from sqlalchemy.exc import NoResultFound

from ..authorizer import token_auth
from ..models.market_day import Market_day as MarketDay
from ..models.ohlcv import Ohlcv as OHLCV
from ..models.stocks import Stocks as Stock
from ..serializers.ohlcv import OhlcvSchema

market_day_routes = Blueprint(__name__)

def initialize_ohlcv(market_day_id):
    all_stocks = Stock.all()
    for stock in all_stocks:
        OHLCV.create(
            market_id=market_day_id,
            stocks_id=stock.id,
            open=-1,
            high=-1,
            low=-1,
            close=-1,
            volume=0
        )
    print("ohlcv successfully created")

@leangle.describe.tags(["Market"])
@leangle.describe.response(204, description='Market open')
@market_day_routes.route('/open', methods=['POST'], cors=True,  authorizer=token_auth)
def open_market():

    """
    Opens the market
    """
    all_days = MarketDay.all()
    if len(all_days) > 0 and all_days[-1].status == "OPEN":
        print("length of days is greater than 0")
        raise BadRequestError("Current day must be closed to open a new day")
    if len(all_days) == 0:
        print("length of days is 0")
        new_day = MarketDay.create(day=1, status='OPEN')
    else:
        print("its closed so ok")
        last_day = all_days[-1]
        new_day = MarketDay.create(day=(last_day.day+1), status='OPEN')
    initialize_ohlcv(new_day.id)
    return Response({"data": "Market is now open"}, status_code=204)

@leangle.describe.tags(["Market"])
@leangle.describe.response(204, description='Market closed')
@market_day_routes.route('/close', methods=['POST'], cors=True,  authorizer=token_auth)
def close_market():
    """
    Closes the market

    """

    all_days = MarketDay.all()
    if len(all_days) == 0 or all_days[-1].status == "CLOSED":
        raise BadRequestError("Market day is not open yet")
    last_day = all_days[-1]
    last_day.update(status="CLOSED")
    return Response({}, status_code=204)

@leangle.describe.tags(["Market"])
@leangle.describe.response(204, description='Market closed', schema='OHLCVResponseSchema')
@market_day_routes.route('/ohlc', methods=['GET'], cors=True)
def get_ohlcv():

    """
    Gets a users OHLCV 
    
    """
    if not market_day_routes.current_request.query_params:
        print("there is no query param ")
        return Response({"data": "Market is now open"}, status_code=400)
    day_num = market_day_routes.current_request.query_params.get('day', None)
    if not day_num:
        print("there is no day value ")
        return Response({"data": "Market is now open"}, status_code=400)
    try:
        day = MarketDay.where(day=day_num).one()
    except NoResultFound as ex:
        return Response({"data": "Market is now open"}, status_code=400)
    ohlcvs = OHLCV.where(market_id=day.id).all()
    print(f"this is the ohlcvs length     {len(ohlcvs)}")
    return_list = []
    for ohlcv in ohlcvs:
        market_day = MarketDay.find_or_fail(ohlcv.market_id)
        stock_name = Stock.find_or_fail(ohlcv.stocks_id)
        obj = {
            'day': market_day.day,
            'stock': stock_name.name,
            'open': ('%.2f' % ohlcv.open),
            'high': ('%.2f' % ohlcv.high),
            'low': ('%.2f' % ohlcv.low),
            'close': ('%.2f' % ohlcv.close),
            'volume': ohlcv.volume,
        }
        return_list.append(obj)
    print(return_list)
    return return_list