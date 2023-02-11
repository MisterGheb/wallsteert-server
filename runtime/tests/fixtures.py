import pytest
import json
from app import app

header = {'Content-Type': 'application/json'}

login_data = json.dumps({
    "email": "jay_vee@trilogy.com",
    "password": "pass"
})
register_data = json.dumps({
    "email": "jay_vee@trilogy.com",
    "password": "pass",
    "username": "jayvee"
})

@pytest.fixture
def gateway_factory():
    from chalice.config import Config
    from chalice.local import LocalGateway

    def create_gateway(config=None):
        if config is None:
            config = Config()
        return LocalGateway(app, config)
    return create_gateway

@pytest.fixture
def user_token(gateway_factory):

    gateway = gateway_factory()
    response = gateway.handle_request(
        method='POST',
        path='/api/v1/auth/login',
        headers={'Content-Type': 'application/json'},
        body=login_data
    )
    json_response = json.loads(response['body'])
    token = json_response['token']
    return token

@pytest.fixture
def sector_id(gateway_factory):
    gateway = gateway_factory()
    response = gateway.handle_request(
        method='GET',
        path='/api/v1/sectors',
        headers=header,
        body=''
    )
    json_response = json.loads(response['body'])
    return json_response[0]['id']

@pytest.fixture
def stock_id(gateway_factory):
    gateway = gateway_factory()
    response = gateway.handle_request(
        method='GET',
        path='/api/v1/stocks/',
        headers=header,
        body=''
    )
    json_response = json.loads(response['body'])
    return json_response[0]['id']

@pytest.fixture
def order_id(gateway_factory, user_token):
    gateway = gateway_factory()
    response = gateway.handle_request(
        method='GET',
        path='/api/v1/orders/',
        headers={'Authorization': f'Bearer {user_token}',**header},
        body=''
    )
    json_response = json.loads(response['body'])
    return json_response[0]['id']

@pytest.fixture
def order(gateway_factory, user_token, stock_id):
    gateway = gateway_factory()
    data = {
        "stock": stock_id,
        "type": "BUY",
        "bid_price": "400.00",
        "bid_volume": 100
    }
    response = gateway.handle_request(
        method='POST',
        path='/api/v1/orders/',
        headers={'Authorization': f'Bearer {user_token}',**header},
        body=json.dumps(data)
    )
    json_response = json.loads(response['body'])
    return json_response

# @pytest.fixture
# def market_day(gateway_factory, user_token):
#     from  ..models.market_day import MarketDay
#     gateway = gateway_factory()
#     response = gateway.handle_request(
#         method='POST',
#         path='/api/v1/market/open',
#         headers={'Authorization': f'Bearer {user_token}',**header},
#         body=''
#     )

#     return json_response