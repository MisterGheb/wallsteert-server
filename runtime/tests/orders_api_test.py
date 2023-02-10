import pytest
import json

from .fixtures import header, gateway_factory, user_token, stock_id, order_id, order


class TestOrders(object):

    def test_buy_order_creation(self, gateway_factory, user_token, stock_id):
        gateway = gateway_factory()
        data = {
            "stocks_id": stock_id,
            "type": "BUY",
            "bid_price": "400.00",
            "bid_volume": 100
        }
        response = gateway.handle_request(
            method='POST',
            path='/api/v1/orders',
            headers={'Authorization': f'Token {user_token}', **header},
            body=json.dumps(data)
        )
        json_response = json.loads(response['body'])
        assert response['statusCode'] == 200
        # assert 'id' in json_response
        assert json_response['status'] == "OPEN"

    def test_list_orders(self, gateway_factory, user_token):
        gateway = gateway_factory()
        response = gateway.handle_request(
            method='GET',
            path='/api/v1/orders',
            headers={'Authorization': f'Token {user_token}', **header},
            body=''
        )
        json_response = json.loads(response['body'])
        assert response['statusCode'] == 200
        assert 'id' in json_response[0]
        assert 'status' in json_response[0]

    def test_retrive_order(self, gateway_factory, user_token, order_id):
        gateway = gateway_factory()
        response = gateway.handle_request(
            method='GET',
            path=f'/api/v1/orders/{order_id}',
            headers={'Authorization': f'Token {user_token}', **header},
            body=''
        )
        json_response = json.loads(response['body'])
        assert response['statusCode'] == 200
        assert 'id' in json_response
        assert 'status' in json_response

    def test_sell_order_creation_fail(self, gateway_factory, user_token, stock_id):
        gateway = gateway_factory()
        data = {
            "stocks_id": stock_id,
            "type": "SELL",
            "bid_price": "350.00",
            "bid_volume": 50
        }
        response = gateway.handle_request(
            method='POST',
            path='/api/v1/orders',
            headers={'Authorization': f'Token {user_token}', **header},
            body=json.dumps(data)
        )
        json_response = json.loads(response['body'])
        assert response['statusCode'] == 400
        assert json_response['Message'] == "Not enough stocks in holding for the operation"
        
    def test_cancel_order(self, gateway_factory, user_token, order):
        gateway = gateway_factory()
        order_id = order['id']
        response = gateway.handle_request(
            method='DELETE',
            path=f'/api/v1/orders/{order_id}/cancel',
            headers={'Authorization': f'Token {user_token}', **header},
            body=''
        )
        assert response['statusCode'] == 204