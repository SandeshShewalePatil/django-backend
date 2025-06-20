from rest_framework import serializers
from .models import Admin, Cart, Order, OrderItem, Product, ProductImage, Address
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password, check_password

# ---------------------------------------------------------------------------------------------------
# admin login check

class AdminLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        try:
            admin = Admin.objects.get(email=email)
        except Admin.DoesNotExist:
            raise serializers.ValidationError('Invalid email')

        # ✅ Secure password check
        if not check_password(password, admin.password):
            raise serializers.ValidationError('Incorrect password')

        # ✅ Return admin object
        data['admin_obj'] = admin
        return data
    
# ---------------------------------------------------------------------------------------------------

# Product Image Serializer
class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image']

# ---------------------------------------------------------------------------------------------------

# Product Serializer with Images
class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'images']

# ---------------------------------------------------------------------------------------------------

# Default User Serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)

# ---------------------------------------------------------------------------------------------------

# Cart Serializer
class CartSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'product', 'product_id', 'quantity', 'subtotal']
        read_only_fields = ['id', 'subtotal']

# ---------------------------------------------------------------------------------------------------

# Address Serializer
class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['full_name', 'phone', 'address', 'city', 'state', 'pincode']

# ---------------------------------------------------------------------------------------------------

# Order Item Serializer
class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_images = ProductImageSerializer(source='product.images', many=True, read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'product_images', 'quantity', 'price']

# ---------------------------------------------------------------------------------------------------

# Order Serializer
class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    address = AddressSerializer()
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user_name', 'user_email', 'address', 'total_price', 'created_at', 'items']

