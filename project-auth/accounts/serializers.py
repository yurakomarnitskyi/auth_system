import jwt
import rest_framework_simplejwt.views as original_views
from authlib.jose import JsonWebKey
from django.conf import settings
from rest_framework_simplejwt.backends import TokenBackend
from rest_framework_simplejwt.serializers import (TokenObtainPairSerializer,
                                                  TokenRefreshSerializer)
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken, Token
from djoser.serializers import UserCreateSerializer
from django.contrib.auth import get_user_model


User = get_user_model()


class UserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ('id', 'email', 'name', 'password')


class TokenBackendWithHeaders(TokenBackend):
    def encode(self, payload, headers={}):
        jwt_payload = payload.copy()
        if self.audience is not None:
            jwt_payload["aud"] = self.audience
        if self.issuer is not None:
            jwt_payload["iss"] = self.issuer

        token = jwt.encode(jwt_payload, self.signing_key,
                           algorithm=self.algorithm, headers=headers)
        if isinstance(token, bytes):
            # For PyJWT <= 1.7.1
            return token.decode("utf-8")
        # For PyJWT >= 2.0.0a1
        return token


class TokenWithAnotherTokenBackend(Token):
    _token_backend = TokenBackendWithHeaders(
        api_settings.ALGORITHM,
        api_settings.SIGNING_KEY,
        api_settings.VERIFYING_KEY,
        api_settings.AUDIENCE,
        api_settings.ISSUER,
        api_settings.JWK_URL,
        api_settings.LEEWAY,
    )

    def __init__(self, token=None, verify=True):
        Token.__init__(self, token, verify)
        self.headers = {}

    def __str__(self):
        return self.get_token_backend().encode(self.payload, self.headers)


class AccessTokenWithAnotherTokenBackend(AccessToken, TokenWithAnotherTokenBackend):
    pass


class RefreshTokenWithAnotherTokenBackend(RefreshToken, TokenWithAnotherTokenBackend):

    @property
    def access_token(self):
        access = AccessTokenWithAnotherTokenBackend()
        access.set_exp(from_time=self.current_time)

        no_copy = self.no_copy_claims
        for claim, value in self.payload.items():
            if claim in no_copy:
                continue
            access[claim] = value

        for claim, value in self.headers.items():
            access.headers[claim] = value

        if 'kid' not in access.headers:
            key = JsonWebKey.import_key(
                settings.SIMPLE_JWT['VERIFYING_KEY'], {'kty': 'RSA'}).thumbprint()
            access.headers['kid'] = key

        return access


class TokenObtainPairSerializerDifferentToken(TokenObtainPairSerializer):
    token_class = RefreshTokenWithAnotherTokenBackend

    @classmethod
    def get_token(cls, user):

        key = JsonWebKey.import_key(
            settings.SIMPLE_JWT['VERIFYING_KEY'], {'kty': 'RSA'})
        token = cls.token_class.for_user(user)

        token.headers['kid'] = key.thumbprint()

        return token


class TokenRefreshSerializerDifferentToken(TokenRefreshSerializer):
    def validate(self, attrs):
        refresh = RefreshTokenWithAnotherTokenBackend(attrs['refresh'])

        data = {'access': str(refresh.access_token)}

        if api_settings.ROTATE_REFRESH_TOKENS:
            if api_settings.BLACKLIST_AFTER_ROTATION:
                try:
                    refresh.blacklist()
                except AttributeError:
                    pass

            refresh.set_jti()
            refresh.set_exp()
            refresh.set_iat()

            data['refresh'] = str(refresh)

        return data


class TokenObtainPairView(original_views.TokenObtainPairView):
    serializer_class = TokenObtainPairSerializerDifferentToken


class TokenRefreshView(original_views.TokenRefreshView):
    serializer_class = TokenRefreshSerializerDifferentToken
