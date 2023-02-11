import json
import pytest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from .fixtures import header, gateway_factory, user_token, login_data, register_data



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
            path='/api/v1/auth/signup',
            headers=header,
            body=register_data
        )
        json_response = json.loads(response['body'])
        assert response['statusCode'] == 200

    def test_login(self, gateway_factory):
        gateway = gateway_factory()
        response = gateway.handle_request(
            method='POST',
            path='/api/v1/auth/login',
            headers=header,
            body=login_data
        )
        json_response = json.loads(response['body'])
        assert response['statusCode'] == 200
        assert 'token' in json_response


    def test_fail_login(self, gateway_factory):
        gateway = gateway_factory()
        response = gateway.handle_request(
            method='POST',
            path='/api/v1/auth/login',
            headers=header,
            body="{'email': 'test@email.com', 'password': 'invalid_pass'}"
        )
        assert response['statusCode'] == 400

    def test_fail_login(self, gateway_factory):
        gateway = gateway_factory()
        response = gateway.handle_request(
            method='POST',
            path='/api/v1/auth/login',
            headers=header,
            body="{'email': 'test@email.com', 'password': 'invalid_pass'}"
        )
        assert response['statusCode'] == 400

    def test_authorize_user(self, gateway_factory, user_token):
        gateway = gateway_factory()
        response = gateway.handle_request(
            method='GET',
            path='/api/v1/users/profile',
            headers={'Authorization': f'Token {user_token}'},
            body=''
        )
        assert response['statusCode'] == 200