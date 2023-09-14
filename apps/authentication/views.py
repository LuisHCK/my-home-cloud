from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from .models import Token
from django.conf import settings


class CustomAuthToken(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        user_agent = request.META['HTTP_USER_AGENT']

        # Create token
        token, created = Token.objects.get_or_create(user=user, device=user_agent)

        # token, created = Token.objects.get_or_create(user=user)
        expires = token.created + settings.TOKEN_TTL

        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email,
            'expires': expires.isoformat()
        })
