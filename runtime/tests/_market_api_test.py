import pytest
import json

from .fixtures import header, gateway_factory, user_token, sector_id, stock_id



class TestMarket(object):

    def test_open_market(self, gateway_factory, user_token):
        gateway = gateway_factory()
        response = gateway.handle_request(
            method='POST',
            path='/api/v1/market/open',
            headers={'Authorization': f'Token {user_token}', **header},
            body=''
        )
        assert response['statusCode'] == 204

    def test_open_market_fail(self, gateway_factory, user_token):
        gateway = gateway_factory()
        response = gateway.handle_request(
            method='POST',
            path='/api/v1/market/open',
            headers={'Authorization': f'Token {user_token}', **header},
            body=''
        )
        json_response = json.loads(response['body'])
        assert response['statusCode'] == 400
        assert json_response['Message'] == "Current day must be closed to open a new day"

    def test_close_market(self, gateway_factory, user_token):
        gateway = gateway_factory()
        response = gateway.handle_request(
            method='POST',
            path='/api/v1/market/close',
            headers={'Authorization': f'Token {user_token}', **header},
            body=''
        )
        assert response['statusCode'] == 204

    def test_close_market_fail(self, gateway_factory, user_token):
        gateway = gateway_factory()
        response = gateway.handle_request(
            method='POST',
            path='/api/v1/market/close',
            headers={'Authorization': f'Token {user_token}', **header},
            body=''
        )
        json_response = json.loads(response['body'])
        assert response['statusCode'] == 400
        assert json_response['Message'] == "Market day is not open yet"

    def test_ohlcv(self, gateway_factory, user_token, stock_id):
        gateway = gateway_factory()
        response = gateway.handle_request(
            method='POST',
            path='/api/v1/market/open',
            headers={'Authorization': f'Token {user_token}', **header},
            body=''
        )
        response = gateway.handle_request(
            method='GET',
            path=f'/api/v1/market/ohlcv/?day=1',
            headers={'Authorization': f'Token {user_token}', **header},
            body=''
        )
        json_response = json.loads(response['body'])
        assert response['statusCode'] == 200
        stock_ids = [ohlcv['stock_id'] for ohlcv in json_response]
        assert stock_id in stock_ids
        assert json_response[0]['open'] == -1
        assert json_response[0]['high'] == -1
        assert json_response[0]['low'] == -1
        assert json_response[0]['close'] == -1
        assert json_response[0]['volume'] == 0