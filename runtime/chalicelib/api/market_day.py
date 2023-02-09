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

@leangle.describe.tags(["Market"])
@leangle.describe.response(204, description='Market open')
@market_day_routes.route('/open', methods=['POST'], cors=True,  authorizer=token_auth)
def open_market():
    all_days = MarketDay.all()
    if len(all_days) > 0 and all_days[-1].status == "OPEN":
        raise BadRequestError("Current day must be closed to open a new day")
    if len(all_days) == 0:
        new_day = MarketDay.create(day=0, status='OPEN')
    else:
        last_day = all_days[-1]
        new_day = MarketDay.create(day=(last_day.day+1), status='OPEN')
    initialize_ohlcv(new_day.id)
    return Response({}, status_code=204)

@leangle.describe.tags(["Market"])
@leangle.describe.response(204, description='Market closed')
@market_day_routes.route('/close', methods=['POST'], cors=True,  authorizer=token_auth)
def close_market():
    all_days = MarketDay.all()
    if len(all_days) == 0 or all_days[-1].status == "CLOSED":
        raise BadRequestError("Market day is not open yet")
    last_day = all_days[-1]
    last_day.update(status="CLOSED")
    return Response({}, status_code=204)

@leangle.describe.tags(["Market"])
@leangle.describe.response(204, description='Market closed', schema='OHLCVResponseSchema')
@market_day_routes.route('/ohlcv', methods=['GET'], cors=True)
def get_ohlcv():
    if not market_day_routes.current_request.query_params:
        raise BadRequestError("Missing required 'day' parameter")
    day_num = market_day_routes.current_request.query_params.get('day', None)
    if not day_num:
        raise BadRequestError("Missing required 'day' parameter")
    try:
        day = MarketDay.where(day=day_num).one()
    except NoResultFound as ex:
        raise BadRequestError("Day does not exist")
    ohlcvs = OHLCV.where(market=day.id).all()
    return_list = []
    for ohlcv in ohlcvs:
        market_day = MarketDay.find_or_fail(ohlcv.market)
        obj = {
            'day': market_day.day,
            'stock': ohlcv.stock,
            'open': ohlcv.open,
            'high': ohlcv.high,
            'low': ohlcv.low,
            'close': ohlcv.close,
            'volume': ohlcv.volume,
        }
        return_list.append(obj)
    return return_list