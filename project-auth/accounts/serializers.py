import jwt
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
        """Returns an encoded token for the given
        payload and headers dictionaries."""
        jwt_payload = payload.copy()
        if self.audience is not None:
            jwt_payload["aud"] = self.audience
        if self.issuer is not None:
            jwt_payload["iss"] = self.issuer

        token = jwt.encode(jwt_payload, self.signing_key,
                           algorithm=self.algorithm, headers=headers)
        if isinstance(token, bytes):
            return token.decode("utf-8")
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
        """Add headers to default Token"""
        Token.__init__(self, token, verify)
        self.headers = {}

    def __str__(self):
        """Sign and return a token."""
        return self.get_token_backend().encode(self.payload, self.headers)


class AccessTokenWithAnotherTokenBackend(AccessToken, TokenWithAnotherTokenBackend):
    pass


class RefreshTokenWithAnotherTokenBackend(RefreshToken, TokenWithAnotherTokenBackend):
    @property
    def access_token(self):
        """
        Returns an access token created from this refresh
        token. Add 'kid' into a header of new token.
        """
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
        """Add 'kid' into a header of new token."""
        key = JsonWebKey.import_key(
            settings.SIMPLE_JWT['VERIFYING_KEY'], {'kty': 'RSA'})
        token = cls.token_class.for_user(user)
        token.headers['kid'] = key.thumbprint()
        return token


class TokenRefreshSerializerDifferentToken(TokenRefreshSerializer):
    def validate(self, attrs):
        """Validate token's data"""
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
