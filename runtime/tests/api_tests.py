import json
import pytest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from app import app

register_data = json.dumps({
    "email": "vaibhav.goyal@trilogy.com",
    "password1": "pass"
})
login_data = json.dumps({
    "email": "vaibhav.goyal@trilogy.com",
    "password": "pass"
})


header = {'Content-Type': 'application/json'}

@pytest.fixture
def gateway_factory():
    from chalice.config import Config
    from chalice.local import LocalGateway

    def create_gateway(config=None):
        if config is None:
            config = Config()
        return LocalGateway(app, config)
    return create_gateway


class TestUsers(object):

    def test_health_check(self, gateway_factory):
        gateway = gateway_factory()
        response = gateway.handle_request(
            method='GET',
            path='/healthcheck',
            headers={},
            body=''
        )
        assert response['statusCode'] == 200
        assert json.loads(response['body']) == dict([('status', 'healthy')])

    def test_register(self, gateway_factory):
        gateway = gateway_factory()
        response = gateway.handle_request(
            method='POST',
            path='/auth/registration',
            headers=header,
            body=register_data
        )
        json_response = json.loads(response['body'])
        assert response['statusCode'] == 200
        assert 'key' in json_response

    def test_login(self, gateway_factory):
        gateway = gateway_factory()
        response = gateway.handle_request(
            method='POST',
            path='/auth/login',
            headers=header,
            body=login_data
        )
        json_response = json.loads(response['body'])
        assert response['statusCode'] == 200
        assert 'key' in json_response


    def test_fail_login(self, gateway_factory):
        gateway = gateway_factory()
        response = gateway.handle_request(
            method='POST',
            path='/auth/login',
            headers=header,
            body=register_data
        )
        assert response['statusCode'] == 400



    def test_authorize_user(self, gateway_factory):
        gateway = gateway_factory()
        response = gateway.handle_request(
            method='POST',
            path='/auth/login',
            headers=header,
            body=login_data
        )
        json_response = json.loads(response['body'])
        print(json_response)
        user_token = json_response['key']
        response = gateway.handle_request(
            method='GET',
            path='/auth/user',
            headers={'Authorization': f'Token {user_token}'},
            body=''
        )
        assert response['statusCode'] == 200
