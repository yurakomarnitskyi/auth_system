from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from authlib.jose import JsonWebKey


@api_view(['GET'])
@authentication_classes([])
@permission_classes([AllowAny])
def request_public_key(request):
    key = JsonWebKey.import_key(
        settings.SIMPLE_JWT['VERIFYING_KEY'], {'kty': 'RSA'})
    public_key_pem = settings.PUBLIC_KEY_PEM
    jwk_public_key = {
        "kty": "RSA",
        "kid": key.thumbprint(),
        "n": str(public_key_pem.public_numbers().n),
        "e": str(public_key_pem.public_numbers().e),
        "alg": "RS256"
    }
    return Response({'keys': [jwk_public_key]}, status=status.HTTP_200_OK)
