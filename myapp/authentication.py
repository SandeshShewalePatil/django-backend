import jwt
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings
from myapp.models import Admin

class AdminJWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')

        if not auth_header:
            return None

        try:
            token_type, token = auth_header.split(' ')

            if token_type != 'Bearer':
                raise AuthenticationFailed('Invalid token header.')

            # ✅ SimpleJWT नाही, आपलं manual jwt आहे म्हणून direct decode कर
            decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            print("Decoded token:", decoded_token)

            if not decoded_token.get('is_admin'):
                raise AuthenticationFailed('Invalid admin token.')

            admin_id = decoded_token['id']

            try:
                admin = Admin.objects.get(id=admin_id)
            except Admin.DoesNotExist:
                raise AuthenticationFailed('Admin not found.')

            # ✅ ही line add कर
            admin.is_authenticated = True  # ✅ सगळं काम करणार

            return (admin, None)

        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token expired.')
        except jwt.DecodeError:
            raise AuthenticationFailed('Invalid token.')
        except Exception:
            raise AuthenticationFailed('Invalid token.')
