import logging
import leangle
from chalice import Blueprint, UnauthorizedError

from ..authorizer import token_auth
from ..models.user import User
from ..models.note import Note
from ..serializers.note import NoteSchema

note_routes = Blueprint(__name__)
logger = logging.getLogger(__name__)

@leangle.describe.tags(["Notes"])
@leangle.describe.response(200, description='User Notes', schema='NoteSchema')
@note_routes.route('/', methods=['GET'], cors=True, authorizer=token_auth )
def get_all_notes():
    user_id = note_routes.current_request.context['authorizer']['principalId']
    user = User.find_or_fail(user_id)
    return NoteSchema().dump(user.notes, many=True)

@leangle.describe.tags(["Notes"])
@leangle.describe.parameter(name='body', _in='body', description='Create a new note', schema='NoteSchema')
@leangle.describe.response(200, description='Created', schema='NoteSchema')
@note_routes.route('/', methods=['POST'], cors=True, authorizer=token_auth )
def create_note():
    user_id = note_routes.current_request.context['authorizer']['principalId']
    json_body = note_routes.current_request.json_body
    note_data = NoteSchema().load(json_body)
    note = Note.create(**note_data, created_by_id=user_id)
    return NoteSchema().dump(note)

@leangle.describe.tags(["Notes"])
@leangle.describe.response(200, description='User Note', schema='NoteSchema')
@note_routes.route('/{id}', methods=['GET'], cors=True, authorizer=token_auth )
def get_note(id):
    user_id = note_routes.current_request.context['authorizer']['principalId']
    note = Note.find_or_fail(id)
    if note.created_by_id != int(user_id):
        raise UnauthorizedError(f"User is not allowed to access this note")
    return NoteSchema().dump(note)

@leangle.describe.tags(["Notes"])
@leangle.describe.parameter(name='body', _in='body', description='Update a note', schema='NoteSchema')
@leangle.describe.response(200, description='Note Updated', schema='NoteSchema')
@note_routes.route('/{id}', methods=['PUT'], cors=True, authorizer=token_auth )
def update_note(id):
    user_id = note_routes.current_request.context['authorizer']['principalId']
    json_body = note_routes.current_request.json_body
    note = Note.find_or_fail(id)
    if note.created_by_id != int(user_id):
        raise UnauthorizedError(f"User is not allowed to update this note")
    
    if 'content' in json_body:
        note.update(content = json_body['content'])
    return NoteSchema().dump(note)

@leangle.describe.tags(["Notes"])
@leangle.describe.response(200, description='Note Deleted', schema='NoteSchema')
@note_routes.route('/{id}', methods=['DELETE'], cors=True, authorizer=token_auth )
def delete_note(id):
    user_id = note_routes.current_request.context['authorizer']['principalId']
    note = Note.find_or_fail(id)
    if note.created_by_id != int(user_id):
        raise UnauthorizedError(f"User is not allowed to delete this note")
    note.delete()
    return NoteSchema().dump(note)
