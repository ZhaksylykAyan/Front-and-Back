from urllib.parse import parse_qs
from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from jwt import decode as jwt_decode
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()

@database_sync_to_async
def get_user(validated_token):
    try:
        jwt_auth = JWTAuthentication()
        user = jwt_auth.get_user(validated_token)
        return user
    except Exception:
        return AnonymousUser()

class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        try:
            query_string = scope['query_string'].decode()
            token = parse_qs(query_string).get('token')
            if token:
                validated_token = UntypedToken(token[0])
                scope['user'] = await get_user(validated_token)
            else:
                scope['user'] = AnonymousUser()
        except Exception:
            scope['user'] = AnonymousUser()
        return await super().__call__(scope, receive, send)
