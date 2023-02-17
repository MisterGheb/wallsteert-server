import pytest
import json

from .fixtures import header, gateway_factory, user_token, sector_id


class TestSectors(object):

    def test_create_sector(self, gateway_factory, user_token):
        gateway = gateway_factory()
        data = {
            "name": "Energy",
	        "description": "Energy sector companies"
        }
        response = gateway.handle_request(
            method='POST',
            path='/api/v1/sectors',
            headers={'Authorization': f'Token {user_token}', **header},
            body=json.dumps(data)
        )
        json_response = json.loads(response['body'])
        assert response['statusCode'] == 200
        assert 'description' in json_response
        assert 'id' in json_response
        assert 'name' in json_response

    def test_list_sectors(self, gateway_factory):
        gateway = gateway_factory()
        response = gateway.handle_request(
            method='GET',
            path='/api/v1/sectors',
            headers=header,
            body=''
        )
        json_response = json.loads(response['body'])
        assert response['statusCode'] == 200
        assert 'description' in json_response[0]
        assert 'id' in json_response[0]
        assert 'name' in json_response[0]
        self.sector_id = json_response[0]['id']
    
    def test_retrieve_sector(self, gateway_factory, sector_id):
        gateway = gateway_factory()
        response = gateway.handle_request(
            method='GET',
            path=f'/api/v1/sectors/{sector_id}',
            headers=header,
            body=''
        )
        json_response = json.loads(response['body'])
        assert response['statusCode'] == 200
        assert 'description' in json_response
        assert 'id' in json_response
        assert 'name' in json_response

    def test_update_sector(self, gateway_factory, user_token, sector_id):
        gateway = gateway_factory()
        response = gateway.handle_request(
            method='PATCH',
            path=f'/api/v1/sectors/{sector_id}',
            headers={'Authorization': f'Token {user_token}', **header},
            body='{"description": "TEST"}'
        )
        json_response = json.loads(response['body'])
        assert response['statusCode'] == 200
        assert 'description' in json_response
        assert 'id' in json_response
        assert 'name' in json_response
        response = gateway.handle_request(
            method='GET',
            path=f'/api/v1/sectors/{sector_id}',
            headers={'Authorization': f'Token {user_token}', **header},
            body=''
        )
        json_response = json.loads(response['body'])
        assert response['statusCode'] == 200
        assert json_response['description'] == "TEST"