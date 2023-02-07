import logging
import leangle
from chalice import Blueprint, BadRequestError, UnauthorizedError, Response
from sqlalchemy.exc import NoResultFound

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
    all_orders = Order.where(user=user_id).all()
    return OrderSchema().dump(all_orders, many=True)

@leangle.describe.tags(["Order"])
@leangle.describe.parameter(name='body', _in='body', description='Create a new order', schema='OrderSchema')
@leangle.describe.response(201, description='Created', schema='OrderSchema')
@orders_routes.route('/', methods=['POST'], cors=True, authorizer=token_auth )
def create_order():
    user_id = orders_routes.current_request.context['authorizer']['principalId']
    user = User.find_or_fail(user_id)

    json_body = orders_routes.current_request.json_body
    order_data = OrderSchema().load(json_body)
    total_order_price = float(order_data['bid_price'])*order_data['bid_volume']
    if order_data['order_type'] == 'BUY' and user.available_funds < total_order_price:
        raise BadRequestError("Not enough available funds for the operation")

    if order_data['order_type'] == 'SELL':
        try:
            user_holding = Holding.where(user=user_id, stock=order_data['stock']).one()
        except NoResultFound as ex:
            raise BadRequestError("Not enough stocks in holding for the operation")
        if user_holding.volume < order_data['bid_volume']:
            raise BadRequestError("Not enough stocks in holding for the operation")
        # check to see if user has enough stocks

    order = Order.create(**order_data, user=user_id, executed_volume=0, status='OPEN')
    new_available_funds = float(user.available_funds) - total_order_price
    new_blocked_funds = float(user.blocked_funds) + total_order_price
    user.update(available_funds=new_available_funds, blocked_funds=new_blocked_funds)
    return OrderSchema().dump(order)

@leangle.describe.tags(["Order"])
@leangle.describe.response(200, description='Stock', schema='OrderSchema')
@orders_routes.route('/{id}', methods=['GET'], cors=True, authorizer=token_auth)
def get_order(id):
    user_id = orders_routes.current_request.context['authorizer']['principalId']
    order = Order.find_or_fail(id)
    if order.user != int(user_id):
        raise UnauthorizedError("User is not allowed to access this note")
    return OrderSchema().dump(order)

@leangle.describe.tags(["Order"])
@leangle.describe.response(204, description='Order cancelled', schema='OrderSchema')
@orders_routes.route('/{id}/cancel', methods=['DELETE'], cors=True, authorizer=token_auth )
def cancel_order(id):
    user_id = orders_routes.current_request.context['authorizer']['principalId']
    order = Order.find_or_fail(id)
    if order.user != int(user_id):
        raise UnauthorizedError("User is not allowed to cancel this order")
    order.update(status="CANCELLED")
    reclaimed_funds = float(order.bid_price) * order.bid_volume
    user = User.find_or_fail(user_id)
    user.update(available_funds=user.available_funds+reclaimed_funds, blocked_funds=user.blocked_funds-reclaimed_funds)
    return Response({}, status_code=204)


def close_order(order: Order, trade_price):
    # close the order:
    order.update(status="CLOSED")
    # remove funds from buyer:
    buyer = User.find_or_fail(order.user)
    funds_lost = order.bid_volume*float(trade_price)
    buyer.update(blocked_funds = float(buyer.blocked_funds) - funds_lost)
    # update holdings: # WHEN order_type == 'BUY'
    buyer_holding = Holding.create(
        user=buyer.id, 
        stock=order.stock, 
        volume=order.bid_volume,
        bid_price=order.bid_price
    )
    # update OHLCV
    market_day = MarketDay.where(status='OPEN').first()
    ohlcv = OHLCV.where(market=market_day.id, stock=order.stock).first()
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
@orders_routes.route('/match', methods=['POST'], cors=True, authorizer=token_auth )
def match_orders():
    days = MarketDay.all()
    if len(days) == 0 or days[-1].status == 'CLOSED':
        raise BadRequestError('Market is closed')

    def get_price(e: Order):
        return e.bid_price
    all_open_orders = Order.where(status="OPEN").all()
    all_stock_ids = list(set(order.stock for order in all_open_orders))
    for stock_id in all_stock_ids:
        stock = Stock.find_or_fail(stock_id)
        buy_orders = [order for order in all_open_orders if order.order_type == "BUY"]
        sell_orders = [order for order in all_open_orders if order.order_type == "SELL"]
        buy_orders.sort(reverse=True, key=get_price)
        sell_orders.sort(key=get_price)
        while (len(buy_orders) > 0 and ((len(sell_orders) > 0 and 
                buy_orders[0].bid_price >= sell_orders[0].bid_price) or buy_orders[0].bid_price >= stock.price)):
            # iterating thru buy orders from the largest bid to the cheapest
            buy_order = buy_orders[0]
            if len(sell_orders) > 0 and buy_order.bid_price >= sell_orders[0].bid_price: # trade happening with seller
                sell_order = sell_orders[0]
                trade_amount = min((buy_order.bid_volume - buy_order.executed_volume), (sell_order.bid_volume - sell_order.executed_volume))
                buy_order.update(executed_volume = buy_order.executed_volume + trade_amount)
                sell_order.update(executed_volume = sell_order.executed_volume + trade_amount)
                trade_price = buy_order.bid_price if buy_order.created_at > sell_order.created_at else sell_order.bid_price
                # one of them has executed_volume == bid_volume -> should be closed and the user's funds and holdings updated
                if buy_order.executed_volume == buy_order.bid_volume:
                    close_order(buy_order, trade_price)
                    buy_orders.pop(0)
                if sell_order.executed_volume == sell_order.bid_volume:
                    close_order(sell_order, trade_price)
                    sell_orders.pop(0)
            elif buy_orders[0].bid_price >= stock.price: # trade happening directly with company
                trade_amount = min(stock.unallocated, (buy_order.bid_volume - buy_order.executed_volume))
                # move unallocated stocks to fulfill order
                stock.update(unallocated=stock.unallocated-trade_amount, price=buy_order.bid_price)
                buy_order.update(executed_volume=buy_order.executed_volume + trade_amount)
                if buy_order.executed_volume == buy_order.bid_volume:
                    close_order(buy_order, stock.price)
                    buy_orders.pop(0)

    return Response({}, status_code=200)