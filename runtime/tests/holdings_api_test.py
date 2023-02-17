import pytest
import json

from .fixtures import header, gateway_factory, user_token, stock_id, order_id, order

class TestHoldings(object):

    def test_empty_holdings(self, gateway_factory, user_token):
        gateway = gateway_factory()
        response = gateway.handle_request(
            method='GET',
            path='/api/v1/holdings',
            headers={'Authorization': f'Token {user_token}', **header},
            body=''
        )
        assert response['statusCode'] == 200