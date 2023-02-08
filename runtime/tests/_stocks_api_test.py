# import pytest
# import json

# from .fixtures import header, gateway_factory, user_token, sector_id, stock_id


# class TestStocks(object):

#     def test_create_stock(self, gateway_factory, user_token, sector_id):
#         gateway = gateway_factory()
#         data = {
#             "name": "TSLA",
#             "price": "200.00",
#             "sector": sector_id,
#             "unallocated": 300000,
#             "total_volume": 3000000
#         }
#         response = gateway.handle_request(
#             method='POST',
#             path='/api/v1/stocks',
#             headers={'Authorization': f'Token {user_token}', **header},
#             body=json.dumps(data)
#         )
#         json_response = json.loads(response['body'])
#         assert response['statusCode'] == 201
#         assert 'name' in json_response
#         assert 'id' in json_response
# #
#     def test_list_stocks(self, gateway_factory):
#         gateway = gateway_factory()
#         response = gateway.handle_request(
#             method='GET',
#             path='/api/v1/stocks',
#             headers=header,
#             body=''
#         )
#         json_response = json.loads(response['body'])
#         assert response['statusCode'] == 200
#         assert 'name' in json_response[0]
#         assert 'unallocated' in json_response[0]
#         assert 'id' in json_response[0]

#     def test_retrieve_stock(self, gateway_factory, stock_id):
#         gateway = gateway_factory()
#         response = gateway.handle_request(
#             method='GET',
#             path=f'/api/v1/stocks/{stock_id}',
#             headers=header,
#             body=''
#         )
#         json_response = json.loads(response['body'])
#         assert response['statusCode'] == 200
#         assert 'unallocated' in json_response
#         assert 'id' in json_response
#         assert 'name' in json_response