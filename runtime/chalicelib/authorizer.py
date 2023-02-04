from chalice import Blueprint, AuthResponse

from .models.users import Users

auth_blueprint = Blueprint(__name__)

@auth_blueprint.authorizer()
def token_auth(auth_request):
    token = auth_request.token.split()[1]
    user_id = User.where(token = token).first().id
    return AuthResponse(routes=['*'], principal_id=user_id)
