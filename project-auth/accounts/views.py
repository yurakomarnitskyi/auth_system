import json

from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from jwcrypto import jwk


@api_view(['GET'])
@authentication_classes([])
@permission_classes([AllowAny])
def request_public_key(request) -> Response:
    """Provide JWK endpoint

    Need for validating tokens on API
    gateway level"""
    jwk_export = jwk.JWK.from_pem(settings.PUBLIC_KEY_PEM.encode('latin-1')).export()
    return Response({'keys': [json.loads(jwk_export)]}, status=status.HTTP_200_OK)
