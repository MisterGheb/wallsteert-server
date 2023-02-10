import logging
import leangle
from chalice import Blueprint, BadRequestError, UnauthorizedError, Response
from sqlalchemy.exc import NoResultFound
from datetime import datetime, date, timezone, time
import time
from json import JSONEncoder

from ..authorizer import token_auth
from ..models.orders import Orders as Order
from ..models.stocks import Stocks as Stock
from ..models.users import Users as User
from ..models.holdings import Holdings as Holding
from ..models.market_day import Market_day as MarketDay
from ..models.ohlcv import Ohlcv as OHLCV
from ..serializers.orders import OrdersSchema as OrderSchema

orders_routes = Blueprint(__name__)
logger = logging.getLogger(__name__)


@leangle.describe.tags(["Order"])
@leangle.describe.response(200, description='Orders', schema='OrderSchema')
@orders_routes.route('/', methods=['GET'], cors=True,  authorizer=token_auth)
def list_orders():
    user_id = orders_routes.current_request.context['authorizer']['principalId']
    all_orders = Order.where(users_id=user_id).all()
    return_orders = []
    for order in all_orders:
        return_orders.append({
            "id": order.id,
            "stock": order.stocks_id,
            "user": order.users_id,
            "type": order.type,
            "bid_price": order.bid_price,
            "bid_volume": order.bid_volume,
            "executed_volume": order.executed_volume,
            "status": order.status,
            "created_at": str(order.created_at),
            "updated_at": str(order.updated_at)
        })
    return return_orders


@leangle.describe.tags(["Order"])
@leangle.describe.parameter(name='body', _in='body', description='Create a new order', schema='OrderSchema')
@leangle.describe.response(201, description='Created', schema='OrderSchema')
@orders_routes.route('/', methods=['POST'], cors=True, authorizer=token_auth)
def create_order():
    user_id = orders_routes.current_request.context['authorizer']['principalId']
    user = User.find_or_fail(user_id)

    json_body = orders_routes.current_request.json_body
    order_data = OrderSchema().load(json_body)
    total_order_price = float(order_data['bid_price'])*order_data['bid_volume']
    if order_data['type'] == 'BUY' and user.available_funds < total_order_price:
        raise BadRequestError("Not enough available funds for the operation")

    if order_data['type'] == 'SELL':
        try:
            user_holding = Holding.where(
                users_id=user_id, stocks_id=order_data['stocks_id']).one()
        except NoResultFound as ex:
            raise BadRequestError(
                "Not enough stocks in holding for the operation 1")
        if user_holding.volume < order_data['bid_volume']:
            raise BadRequestError(
                "Not enough stocks in holding for the operation")
        # check to see if user has enough stocks
    timestamp = time.time()
    dt_object = datetime.fromtimestamp(timestamp)
    print(order_data["stock"])
    order = Order.create(type=order_data['type'], bid_price=order_data["bid_price"], bid_volume=order_data["bid_volume"],
                         stocks_id=order_data['stock'], users_id=user_id, executed_volume=0, status='OPEN', created_at=dt_object, updated_at=dt_object)
    new_available_funds = float(user.available_funds) - total_order_price
    new_blocked_funds = float(user.blocked_funds) + total_order_price
    user.update(available_funds=new_available_funds,
                blocked_funds=new_blocked_funds)

    return_order = {
        "id": order.id,
        "stock": order.stocks_id,
        "user": order.users_id,
        "type": order.type,
        "bid_price": order.bid_price,
        "bid_volume": order.bid_volume,
        "executed_volume": order.executed_volume,
        "status": order.status,
        "created_at": str(order.created_at),
        "updated_at": str(order.updated_at)
    }
    return Response(return_order, status_code=201)


@leangle.describe.tags(["Order"])
@leangle.describe.response(200, description='Stock', schema='OrderSchema')
@orders_routes.route('/{id}', methods=['GET'], cors=True, authorizer=token_auth)
def get_order(id):
    user_id = orders_routes.current_request.context['authorizer']['principalId']
    order = Order.find_or_fail(id)
    if order.users_id != int(user_id):
        raise UnauthorizedError("User is not allowed to access this note")

    return_order = {
        "id": order.id,
        "stock": order.stocks_id,
        "user": order.users_id,
        "type": order.type,
        "bid_price": order.bid_price,
        "bid_volume": order.bid_volume,
        "executed_volume": order.executed_volume,
        "status": order.status,
        "created_at": str(order.created_at),
        "updated_at": str(order.updated_at)
    }
    return return_order


@leangle.describe.tags(["Order"])
@leangle.describe.response(200, description='Order cancelled', schema='OrderSchema')
@orders_routes.route('/{id}/cancel', methods=['DELETE'], cors=True, authorizer=token_auth)
def cancel_order(id):
    user_id = orders_routes.current_request.context['authorizer']['principalId']
    order = Order.find_or_fail(id)
    if order.users_id != int(user_id):
        raise UnauthorizedError("User is not allowed to cancel this order")
    order.update(status="CANCELLED")
    reclaimed_funds = order.bid_price * order.bid_volume
    user = User.find_or_fail(user_id)
    user.update(available_funds=user.available_funds+reclaimed_funds,
                blocked_funds=user.blocked_funds-reclaimed_funds)
    return Response("", status_code=204)


def close_order(order: Order, trade_price):
    # close the order:
    order.update(status="CLOSED")
    # remove funds from buyer:
    buyer = User.find_or_fail(order.users_id)
    funds_lost = order.bid_volume*float(trade_price)
    buyer.update(blocked_funds=float(buyer.blocked_funds) - funds_lost)
    # update holdings: # WHEN order_type == 'BUY'
    print("it got here")

    buyer_holding = Holding.create(
        users_id=buyer.id,
        stocks_id=order.stocks_id,
        volume=order.bid_volume,
        bid_price=145,
        bought_on=date.today()
    )
    # Currently not working
    print(buyer_holding)
    # update OHLCV
    market_day = MarketDay.where(status='OPEN').first()
    ohlcv = OHLCV.where(market_id=market_day.id,
                        stocks_id=order.stocks_id).first()
    open = trade_price if ohlcv.open == -1 else ohlcv.open
    high = trade_price if ohlcv.high < trade_price else ohlcv.high
    low = trade_price if ohlcv.low > trade_price or ohlcv.low == -1 else ohlcv.low
    ohlcv.update(
        open=open,
        high=high,
        low=low,
        close=trade_price,
        volume=ohlcv.volume+order.bid_volume
    )


@leangle.describe.tags(["Order"])
@leangle.describe.response(200, description='Orders matched')
@orders_routes.route('/match', methods=['POST'], cors=True, authorizer=token_auth)
def match_orders():
    days = MarketDay.all()
    if len(days) == 0 or days[-1].status == 'CLOSED':
        # if the market is closed then you can not match orders
        raise BadRequestError('Sorry market is closed try again when it opens')

    def get_price(e: Order):
        return e.bid_price  # bid price for the order
    all_open_orders = Order.where(
        status="OPEN").all()  # get all the open orders
    # get all the unique stocks in the open orders
    all_stock_ids = list(set(order.stocks_id for order in all_open_orders))
    for stock_id in all_stock_ids:
        # find the stock in stocks table looped
        stock = Stock.find_or_fail(stock_id)
        # all the buy orders
        buy_orders = [
            order for order in all_open_orders if order.type == "BUY"]
        # all the sell orders
        sell_orders = [
            order for order in all_open_orders if order.type == "SELL"]
        # listing from highest to lowest
        buy_orders.sort(reverse=True, key=get_price)
        sell_orders.sort(key=get_price)  # lowest to highest
        print(1)
        while (len(buy_orders) > 0 and ((len(sell_orders) > 0 and
                                         buy_orders[0].bid_price >= sell_orders[0].bid_price) or buy_orders[0].bid_price >= stock.price)):
            # iterating thru buy orders from the largest bid to the cheapest
            buy_order = buy_orders[0]
            print(2)
            # trade happening with seller
            if len(sell_orders) > 0 and buy_order.bid_price >= sell_orders[0].bid_price:
                sell_order = sell_orders[0]
                trade_amount = min((buy_order.bid_volume - buy_order.executed_volume), (sell_order.bid_volume -
                                   sell_order.executed_volume))  # see how many stocks need to be traded
                # update buyed executed amount
                buy_order.update(
                    executed_volume=buy_order.executed_volume + trade_amount)
                # update seller executed amount
                sell_order.update(
                    executed_volume=sell_order.executed_volume + trade_amount)
                trade_price = buy_order.bid_price if buy_order.created_at > sell_order.created_at else sell_order.bid_price
                # one of them has executed_volume == bid_volume -> should be closed and the user's funds and holdings updated
                print(3)
                # if buyer has no more stocks needed to buy, close order
                if buy_order.executed_volume == buy_order.bid_volume:
                    # if buyer has no more stocks needed to buy, close order
                    close_order(buy_order, trade_price)
                    buy_orders.pop(0)
                    print(4)
                if sell_order.executed_volume == sell_order.bid_volume:
                    close_order(sell_order, trade_price)
                    sell_orders.pop(0)  # same thing for seller
                    print(5)
            # trade happening directly with company
            elif buy_orders[0].bid_price >= stock.price:
                trade_amount = min(
                    stock.unallocated, (buy_order.bid_volume - buy_order.executed_volume))
                # move unallocated stocks to fulfill order
                stock.update(unallocated=stock.unallocated -
                             trade_amount, price=buy_order.bid_price)
                buy_order.update(
                    executed_volume=buy_order.executed_volume + trade_amount)
                print(6)
                if buy_order.executed_volume == buy_order.bid_volume:
                    close_order(buy_order, stock.price)
                    buy_orders.pop(0)
                    print(7)
    return Response("", status_code=201)