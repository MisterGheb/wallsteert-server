import logging
import leangle
from chalice import Blueprint, BadRequestError, UnauthorizedError, Response
from sqlalchemy.exc import NoResultFound
from datetime import datetime, date, timezone, time
import time
from json import JSONEncoder

from chalicelib.authorizer import token_auth
from chalicelib.models.order import Order
from chalicelib.models.stock import Stock
from chalicelib.models.user import User
from chalicelib.models.holding import Holding
from chalicelib.models.market_day import MarketDay
from chalicelib.models.ohlcv import OHLCV
from chalicelib.serializers.order import OrderSchema

order_routes = Blueprint(__name__)
logger = logging.getLogger(__name__)


@leangle.describe.tags(["Order"])
@leangle.describe.response(200, description="Orders", schema="OrderSchema")
@order_routes.route("/", methods=["GET"], cors=True, authorizer=token_auth)
def list_orders():
    """
    Returns all orders of the logged in user.
    """
    user_id = order_routes.current_request.context["authorizer"]["principalId"]
    all_orders = Order.where(user=user_id).all()
    return OrderSchema().dump(all_orders, many=True)


@leangle.describe.tags(["Order"])
@leangle.describe.parameter(
    name="body", _in="body", description="Create a new order", schema="OrderSchema"
)
@leangle.describe.response(200, description="Created", schema="OrderSchema")
@order_routes.route("/", methods=["POST"], cors=True, authorizer=token_auth)
def create_order():
    """
    Places a new order in the name of the logged in user,
    blocking the corresponding amount of funds from the user.
    """
    user_id = order_routes.current_request.context["authorizer"]["principalId"]
    user = User.find_or_fail(user_id)

    json_body = order_routes.current_request.json_body
    order_data = OrderSchema().load(json_body)
    try:
        Stock.find_or_fail(order_data["stock"])
    except NoResultFound:
        raise BadRequestError("Stock does not exist")
    total_order_price = float(order_data["bid_price"]) * order_data["bid_volume"]
    if order_data["type"] == "BUY" and user.available_funds < total_order_price:
        raise BadRequestError("Not enough available funds for the operation")

    if order_data["type"] == "SELL":
        try:
            user_holding = Holding.where(user=user_id, stock=order_data["stock"]).one()
        except NoResultFound as ex:
            raise BadRequestError("Not enough stocks in holding for the operation")
        if user_holding.volume < order_data["bid_volume"]:
            raise BadRequestError("Not enough stocks in holding for the operation")
        # check to see if user has enough stocks

    order = Order.create(
        **order_data, user=user_id, executed_volume=0, status="PENDING"
    )
    new_available_funds = float(user.available_funds) - total_order_price
    new_blocked_funds = float(user.blocked_funds) + total_order_price
    user.update(available_funds=new_available_funds, blocked_funds=new_blocked_funds)
    return Response(OrderSchema().dump(order), status_code=200)


@leangle.describe.tags(["Order"])
@leangle.describe.response(200, description="Stock", schema="OrderSchema")
@order_routes.route("/{id}", methods=["GET"], cors=True, authorizer=token_auth)
def get_order(id):
    """
    Retrieves an order by its id.
    """
    user_id = order_routes.current_request.context["authorizer"]["principalId"]
    try:
        order = Order.find_or_fail(id)
    except NoResultFound:
        raise BadRequestError("Order does not exist")
    if order.user != int(user_id):
        raise UnauthorizedError("User is not allowed to access this order")
    return OrderSchema().dump(order)


@leangle.describe.tags(["Order"])
@leangle.describe.response(204, description="Order cancelled", schema="OrderSchema")
@order_routes.route(
    "/{id}/cancel", methods=["DELETE"], cors=True, authorizer=token_auth
)
def cancel_order(id):
    """
    Cancels an order given its id.
    """
    user_id = order_routes.current_request.context["authorizer"]["principalId"]
    try:
        order = Order.find_or_fail(id)
    except NoResultFound:
        raise BadRequestError("Order does not exist")
    if order.user != int(user_id):
        raise UnauthorizedError("User is not allowed to cancel this order")
    order.update(status="CANCELLED")
    reclaimed_funds = float(order.bid_price) * order.bid_volume
    user = User.find_or_fail(user_id)
    user.update(
        available_funds=float(user.available_funds) + reclaimed_funds,
        blocked_funds=float(user.blocked_funds) - reclaimed_funds,
    )
    return Response({}, status_code=204)


def should_keep_matching(buy_orders, sell_orders, stock):
    if len(buy_orders) == 0:
        return False
    can_match_with_seller = (
        len(sell_orders) > 0 and buy_orders[0].bid_price >= sell_orders[0].bid_price
    )
    can_match_with_company = buy_orders[0].bid_price >= stock.price
    return can_match_with_seller or can_match_with_company


def update_ohlcv(stock_id, trade_price):
    """
    Updates OHLCV data for the curret market day after a trade was completed.
    Parameters:
    stock_id: id of the stock which was just traded
    trade_price: price of the trade
    """

    market_reverse = sorted(MarketDay.all(), key=lambda x: x.day, reverse=True)
    market_day = market_reverse[0]

    ohlcv = OHLCV.where(market=market_day.id, stock=stock_id).first()
    open_ = trade_price if ohlcv.open == -1 else ohlcv.open
    high = trade_price if ohlcv.high < trade_price else ohlcv.high
    low = trade_price if ohlcv.low > trade_price or ohlcv.low == -1 else ohlcv.low
    ohlcv.update(
        open=open_,
        high=high,
        low=low,
        close=trade_price,
        volume=ohlcv.volume + trade_amount,
    )


def update_buyer_holdings(buy_order, trade_amount, trade_price):
    """
    Updates a user's holding upon fulfulling (partially or completely) a buy order.
    """
    buyer_holding = Holding.where(user=buy_order.user, stock=buy_order.stock).first()
    if buyer_holding is not None:
        average_bid_price_holding = (
            buyer_holding.volume * float(buyer_holding.bid_price) + trade_amount * float(trade_price)
        ) / (buyer_holding.volume + trade_amount) 
        buyer_holding.update(
            volume=buyer_holding.volume + trade_amount,
            bought_on=date.today(),
            bid_price=average_bid_price_holding,
        )
        return
    Holding.create(
        user=buy_order.user,
        stock=buy_order.stock,
        volume=trade_amount,
        bid_price=trade_price,
        bought_on=date.today(),
    )


def trade_with_seller(buy_order, sell_order, all_buy_orders, all_sell_orders):
    """
    Match a buy order with a sell order.
    The transaction price is determined by whoever placed the order last.
    The corresponding amount of stocks will be moved from the seller's holdings to the buyer's holdings.
    The transaction price will be deducted from the buyer's funds, and added to the seller's funds.
    """
    trade_amount = min(
        (buy_order.bid_volume - buy_order.executed_volume),
        (sell_order.bid_volume - sell_order.executed_volume),
    )
    # update buyed executed amount
    buy_order.update(executed_volume=buy_order.executed_volume + trade_amount)
    # update seller executed amount
    sell_order.update(executed_volume=sell_order.executed_volume + trade_amount)

    buyer_user = User.where(id=buy_order.user).first()
    seller_user = User.where(id=sell_order.user).first()

    trade_price = (
        buy_order.bid_price
        if buy_order.created_at > sell_order.created_at
        else sell_order.bid_price
    )

    buyer_user.update(
        available_funds=buyer_user.available_funds
        + trade_amount * buy_order.bid_price
        - trade_amount * trade_price,
        blocked_funds=buyer_user.blocked_funds - trade_amount * buy_order.bid_price,
    )
    seller_user.update(
        available_funds=seller_user.available_funds + trade_amount * trade_price
    )

    update_buyer_holdings(buy_order, trade_amount, trade_price)

    seller_holding = Holding.where(user=sell_order.user, stock=sell_order.stock).first()
    seller_holding.update(volume=seller_holding.volume - trade_amount)
    update_ohlcv(buy_order.stock, trade_price)

    if buy_order.executed_volume == buy_order.bid_volume:
        # if buyer has no more stocks needed to buy, close order
        buy_order.update(status="COMPLETED")
        all_buy_orders.pop(0)
    if sell_order.executed_volume == sell_order.bid_volume:
        all_sell_order.update(status="COMPLETED")
        all_sell_orders.pop(0)

    return [all_buy_orders, all_sell_orders]


def trade_with_company(buy_order, stock, buy_orders):
    """
    Match a buy order with a company directly.
    The company will move unallocated stocks to fulfill the order.
    The corresponding amount of stocks will be moved to the user's holdings.
    """

    trade_amount = min(
        stock.unallocated, (buy_order.bid_volume - buy_order.executed_volume)
    )
    # move unallocated stocks to fulfill order
    stock.update(
        unallocated=stock.unallocated - trade_amount, price=buy_order.bid_price
    )
    buy_order.update(executed_volume=buy_order.executed_volume + trade_amount)

    buyer_user = User.where(id=buy_order.user).first()
    buyer_user.update(
        blocked_funds=buyer_user.blocked_funds - trade_amount * buy_order.bid_price
    )

    update_buyer_holdings(buy_order, trade_amount, stock.price)

    update_ohlcv(stock.id, stock.price)

    if buy_order.executed_volume == buy_order.bid_volume:
        buy_order.update(status="COMPLETED")
        buy_orders.pop(0)
    return buy_orders


def process_stock_orders(stock_id, all_stock_orders):
    """
    Main algorithm to match orders, fullfills trades between buyers and sellers
    (when available), or between buyers and companies directly.
    """
    stock = Stock.find_or_fail(stock_id)
    buy_orders = [order for order in all_stock_orders if order.type == "BUY"]
    sell_orders = [order for order in all_stock_orders if order.type == "SELL"]
    buy_orders.sort(reverse=True, key=lambda x: x.bid_price)
    sell_orders.sort(key=lambda x: x.bid_price)

    while should_keep_matching(buy_orders, sell_orders, stock):
        # iterating thru buy orders from the largest bid to the cheapest
        buy_order = buy_orders[0]

        if len(sell_orders) > 0:
            sell_order = sell_orders[0]
        # trade happening with seller
        should_trade_with_seller = (
            len(sell_orders) > 0 and buy_order.bid_price >= sell_order.bid_price
        )

        if should_trade_with_seller:
            [buy_orders, sell_orders] = trade_with_seller(buy_order, sell_order)
            continue

        # trade happening directly with company
        if buy_orders[0].bid_price >= stock.price:
            buy_orders = trade_with_company(buy_order, stock, buy_orders)


@leangle.describe.tags(["Order"])
@leangle.describe.response(200, description="Orders matched")
@order_routes.route("/match", methods=["POST"], cors=True, authorizer=token_auth)
def match_orders():
    """
    Triggers the algorithm to match orders for every stock for which at least one order is placed.
    """

    market_reverse = sorted(MarketDay.all(), key=lambda x: x.day, reverse=True)
    if len(market_reverse) == 0:
        raise BadRequestError("market not open")
    elif market_reverse[0].status == "CLOSED":
        raise BadRequestError("market not open")

    all_open_orders = Order.where(status="PENDING").all()
    all_stock_ids = list(set(order.stock for order in all_open_orders))
    for stock_id in all_stock_ids:
        all_stock_orders = [
            order for order in all_open_orders if order.stock == stock_id
        ]
        process_stock_orders(stock_id, all_stock_orders)

    return Response({}, status_code=200)