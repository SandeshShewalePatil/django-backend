from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from myapp.authentication import AdminJWTAuthentication
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from datetime import datetime, timedelta
import jwt
from django.conf import settings
from .models import Cart, Contact, Order, OrderItem, Product , ProductImage
from .serializers import (
    AddressSerializer, AdminLoginSerializer, ContactSerializer, OrderSerializer, ProductSerializer,
    CartSerializer,
)
from .models import Admin

# Admin साठी Login API
class AdminLoginView(APIView):
    def post(self, request):

        # 🔥 Force reset admin every time
        Admin.objects.all().delete()

        Admin.objects.create(
            email="admin@gmail.com",
            password=make_password("123456")
        )

        serializer = AdminLoginSerializer(data=request.data)

        if serializer.is_valid():
            admin_obj = serializer.validated_data['admin_obj']

            payload = {
                'id': admin_obj.id,
                'email': admin_obj.email,
                'exp': datetime.utcnow() + timedelta(days=1),
                'iat': datetime.utcnow(),
                'is_admin': True
            }

            token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

            return Response({
                'access': token,
                'admin': {
                    'id': admin_obj.id,
                    'email': admin_obj.email
                }
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# ---------------------------------------------------------------------------------------------------

# User नोंदणीसाठी API
class RegisterUser(APIView):
    def post(self, request):
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')

        if not username or not email or not password:
            return Response({'message': 'All fields are required'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            return Response({'message': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=email).exists():
            return Response({'message': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create(
            username=username,
            email=email,
            password=make_password(password)
        )

        return Response({'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)
# ---------------------------------------------------------------------------------------------------

# User लॉगिनसाठी API
class LoginUser(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'message': 'Invalid email or password'}, status=status.HTTP_400_BAD_REQUEST)

        authenticated_user = authenticate(username=user.username, password=password)
        if authenticated_user is None:
            return Response({'message': 'Invalid email or password'}, status=status.HTTP_400_BAD_REQUEST)

        refresh = RefreshToken.for_user(user)
        return Response({
            'message': 'Login successful',
            'user_id': user.id,
            'username': user.username,
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        })
# ---------------------------------------------------------------------------------------------------

# सर्व Product साठी ViewSet (Public)
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
# ---------------------------------------------------------------------------------------------------

# Product साठी Multiple Images Upload करण्याची API
class ProductImageUploadView(APIView):
    def post(self, request, format=None):
        product_id = request.data.get('product_id')
        images = request.FILES.getlist('images')

        try:
            product_instance = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

        if not images:
            return Response({'error': 'No images provided'}, status=status.HTTP_400_BAD_REQUEST)

        for img in images:
            ProductImage.objects.create(product=product_instance, image=img)

        return Response({'message': 'Images uploaded successfully'}, status=status.HTTP_201_CREATED)
# ---------------------------------------------------------------------------------------------------

# Product च्या सर्व Images Delete करण्याची API
class DeleteProductImagesView(APIView):
    def delete(self, request, product_id):
        images = ProductImage.objects.filter(product_id=product_id)
        for image in images:
            image.image.delete()
            image.delete()
        return Response({'message': 'Product images deleted successfully.'}, status=status.HTTP_200_OK)
# ---------------------------------------------------------------------------------------------------

# Cart मध्ये Product Add करणे आणि Cart Details मिळवण्यासाठी API
class CartView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        user = request.user
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))

        if not product_id:
            return Response({'error': 'Product ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product_instance = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found.'}, status=status.HTTP_404_NOT_FOUND)

        cart_item, created = Cart.objects.get_or_create(user=user, product=product_instance)
        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        return Response({'message': 'Product added to cart successfully!'}, status=status.HTTP_200_OK)

    def get(self, request):
        user = request.user
        cart_items = Cart.objects.filter(user=user)
        serializer = CartSerializer(cart_items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
# ---------------------------------------------------------------------------------------------------

# Cart मध्ये Product ची Quantity Update करण्याची API
class UpdateCartQuantityView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        cart_id = request.data.get('cart_id')
        quantity = request.data.get('quantity')

        try:
            cart_item = Cart.objects.get(id=cart_id, user=request.user)
            cart_item.quantity = quantity
            cart_item.save()
            return Response({'message': 'Quantity updated successfully'}, status=status.HTTP_200_OK)
        except Cart.DoesNotExist:
            return Response({'message': 'Cart item not found'}, status=status.HTTP_404_NOT_FOUND)
# ---------------------------------------------------------------------------------------------------

# Cart मधून Product Delete करण्याची API
class DeleteCartItemView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def delete(self, request, cart_id):
        try:
            cart_item = Cart.objects.get(id=cart_id, user=request.user)
            cart_item.delete()
            return Response({'message': 'Item removed from cart'}, status=status.HTTP_200_OK)
        except Cart.DoesNotExist:
            return Response({'message': 'Cart item not found'}, status=status.HTTP_404_NOT_FOUND)
# ---------------------------------------------------------------------------------------------------

# Checkout करण्यासाठी (Buy Now किंवा Cart Checkout) API
class CheckoutView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        user = request.user
        checkout_type = request.data.get('checkout_type')  # 'cart' or 'buy_now'
        products = request.data.get('products', [])  # Only for buy now

        if checkout_type == 'buy_now':
            if not products:
                return Response({'error': 'No product provided for Buy Now!'}, status=status.HTTP_400_BAD_REQUEST)

            product_data = products[0]  # We only expect one product for Buy Now
            try:
                product = Product.objects.get(id=product_data['product_id'])
            except Product.DoesNotExist:
                return Response({'error': 'Product not found!'}, status=status.HTTP_400_BAD_REQUEST)

            address_serializer = AddressSerializer(data=request.data)
            if not address_serializer.is_valid():
                return Response(address_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            address = address_serializer.save(user=user)

            order = Order.objects.create(user=user, address=address, total_price=product.price)

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=product_data.get('quantity', 1),
                price=product.price
            )

            return Response({'message': 'Buy Now Order placed successfully!'}, status=status.HTTP_201_CREATED)

        elif checkout_type == 'cart':
            cart_items = Cart.objects.filter(user=user)

            if not cart_items.exists():
                return Response({'error': 'Your cart is empty!'}, status=status.HTTP_400_BAD_REQUEST)

            address_serializer = AddressSerializer(data=request.data)
            if not address_serializer.is_valid():
                return Response(address_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            address = address_serializer.save(user=user)

            total_price = sum(item.product.price * item.quantity for item in cart_items)

            order = Order.objects.create(user=user, address=address, total_price=total_price)

            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.price
                )

            cart_items.delete()

            return Response({'message': 'Cart Order placed successfully!'}, status=status.HTTP_201_CREATED)

        else:
            return Response({'error': 'Invalid checkout type!'}, status=status.HTTP_400_BAD_REQUEST)
# ---------------------------------------------------------------------------------------------------

# User च्या सर्व Order List साठी API
class UserOrdersView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        user = request.user
        orders = Order.objects.filter(user=user).order_by('-created_at')
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)
# ---------------------------------------------------------------------------------------------------

# User चा Order Cancel करण्यासाठी API
class CancelOrderView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def delete(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id, user=request.user)
            order.delete()
            return Response({'message': 'Order cancelled successfully!'}, status=status.HTTP_200_OK)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found!'}, status=status.HTTP_404_NOT_FOUND)
# ---------------------------------------------------------------------------------------------------

# Admin साठी सर्व Orders List मिळवण्याची API
class AdminOrderListView(APIView):
    authentication_classes = [AdminJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            orders = Order.objects.all().order_by('-created_at')
            serializer = OrderSerializer(orders, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            print("Error in fetching orders: ", e)
            return Response({'error': 'Something went wrong'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
# ---------------------------------------------------------------------------------------------------

# Contact Form Submit करण्यासाठी व सर्व Contact List मिळवण्यासाठी API
class ContactView(APIView):
    def post(self, request):
        serializer = ContactSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Contact submitted successfully.'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        contacts = Contact.objects.all().order_by('-created_at')  # Optional: List all contacts
        serializer = ContactSerializer(contacts, many=True)
        return Response(serializer.data)
# ---------------------------------------------------------------------------------------------------

# Contact Data Delete करण्यासाठी API
class ContactDeleteView(APIView):
    def delete(self, request, pk):
        try:
            contact = Contact.objects.get(pk=pk)
            contact.delete()
            return Response({'message': 'Contact deleted successfully.'}, status=status.HTTP_200_OK)
        except Contact.DoesNotExist:
            return Response({'error': 'Contact not found.'}, status=status.HTTP_404_NOT_FOUND)
