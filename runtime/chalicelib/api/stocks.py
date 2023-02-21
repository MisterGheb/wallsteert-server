import logging
import leangle
from chalice import Blueprint, BadRequestError, Response
from sqlalchemy import exc
from marshmallow import exceptions

from .market_day import initialize_ohlcv
from ..models.ohlcv import Ohlcv as OHLCV
from ..authorizer import token_auth
from ..models.market_day import Market_day
from ..models.users import Users as User
from ..models.stocks import Stocks
from ..serializers.stocks import StocksSchema
from ..constants import *

stocks_routes = Blueprint('stocks')
logger = logging.getLogger(__name__)


@leangle.describe.tags(["Stocks"])
@leangle.describe.parameter(
    name='body',
    _in='body',
    description='List all stocks available in the market',
    schema='StocksSchema'
)
@leangle.describe.response(
    200,
    description='Stocks Listed',
    schema='StocksSchema'
)
@stocks_routes.route(
    '/',
    methods=['GET'],
    cors=True
)
def list_stocks():
    stocks = Stocks.all()
    returnStocks = []
    for stock in stocks:
        returnStocks.append({
            "id": stock.id,
            "name": stock.name,
            "price": ('%.2f' % stock.price),
            "sector": stock.sectors_id,
            "unallocated": stock.unallocated,
            "total_volume": stock.total_volume
        })
    return returnStocks


@leangle.describe.tags(["Stocks"])
@leangle.describe.parameter(
    name='body',
    _in='body',
    description='Create a stock in the market',
    schema='StocksSchema'
)
@leangle.describe.response(
    200,
    description='Stock Created',
    schema='StocksSchema'
)
@stocks_routes.route(
    '/',
    methods=['POST'],
    cors=True,
    authorizer=token_auth
)
def create_stock():
    user_id = stocks_routes.current_request.context['authorizer']['principalId']
    user = User.find_or_fail(user_id)

    json_body = stocks_routes.current_request.json_body
    try:
        data_obj = StocksSchema().load(json_body)
    except TypeError as ex:
        raise BadRequestError(ex)
    except exceptions.ValidationError as ex:
        raise BadRequestError(ex)
    print(data_obj)
    try:
        stock = Stocks.create(
            name=data_obj["name"],
            price=data_obj["price"],
            sectors_id=data_obj["sector"],
            unallocated=data_obj["unallocated"],
            total_volume=data_obj["total_volume"]
        )
    except exc.IntegrityError as ex:
        raise BadRequestError(ex._message())

    return_stock = {
        "id": stock.id,
        "name": stock.name,
        "price": stock.price,
        "sector": stock.sectors_id,
        "unallocated": stock.unallocated,
        "total_volume": stock.total_volume
    }
    market_reverse = sorted(
        Market_day.all(), key=lambda x: x.day, reverse=True)
    if market_reverse[0].status == "OPEN":
        OHLCV.create(
            market_id=market_reverse[0].id,
            stocks_id=stock.id,
            open=-1,
            high=-1,
            low=-1,
            close=-1,
            volume=0
        )
    return Response(return_stock, status_code=200)


@leangle.describe.tags(["Stocks"])
@leangle.describe.parameter(
    name='body',
    _in='body',
    description='Get Stock',
    schema='StocksSchema'
)
@leangle.describe.response(
    200,
    description='Stock Retrieved',
    schema='StocksSchema'
)
@stocks_routes.route('/{stock_id}', methods=['GET'], cors=True)
def get_stock(stock_id):
    stock = Stocks.where(id=stock_id).first()
    if(stock == None):
        return Response("", status_code=404)
    return_stock = {
        "id": stock.id,
        "name": stock.name,
        "price": ('%.2f' % stock.price),
        "sector": stock.sectors_id,
        "unallocated": stock.unallocated,
        "total_volume": stock.total_volume
    }
    return return_stock