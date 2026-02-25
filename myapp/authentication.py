import jwt
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings
from myapp.models import Admin

# ✅ Admin साठी JWT Authentication
class AdminJWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')

        if not auth_header:
            return None  # ✅ Header नसेल तर authentication करायचं नाही

        try:
            token_type, token = auth_header.split(' ')

            if token_type != 'Bearer':
                raise AuthenticationFailed('Invalid token header.')  # ✅ Bearer token format चेक

            # ✅ SimpleJWT नाही, आपलं manual jwt आहे म्हणून direct decode कर
            decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            print("Decoded token:", decoded_token)

            if not decoded_token.get('is_admin'):
                raise AuthenticationFailed('Invalid admin token.')  # ✅ Admin flag चेक करतोय

            admin_id = decoded_token['id']

            try:
                admin = Admin.objects.get(id=admin_id)  # ✅ Admin database मधून शोधतोय
            except Admin.DoesNotExist:
                raise AuthenticationFailed('Admin not found.')

            # ✅ Admin ला authenticated mark करतोय
            admin.is_authenticated = True

            return (admin, None)  # ✅ Successful authentication return

        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token expired.')  # ✅ Token expiry चेक
        except jwt.DecodeError:
            raise AuthenticationFailed('Invalid token.')  # ✅ Token decode error
        except Exception:
            raise AuthenticationFailed('Invalid token.')  # ✅ Other unknown error
