from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from myapp.views import (
    AdminLoginView, AdminOrderListView, CancelOrderView, CheckoutView, ProductViewSet, CartView, UpdateCartQuantityView, DeleteCartItemView,
    RegisterUser, LoginUser, ProductImageUploadView, DeleteProductImagesView, UserOrdersView,
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.conf import settings
from django.conf.urls.static import static

router = DefaultRouter()
router.register(r'product', ProductViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', include(router.urls)),

    # Admin login
    path('api/admin-login/', AdminLoginView.as_view()),
    path('api/admin/orders/', AdminOrderListView.as_view()),

    # Product images
    path('upload-images/', ProductImageUploadView.as_view(), name='upload-images'),
    path('delete-product-images/<int:product_id>/', DeleteProductImagesView.as_view(), name='delete_product_images'),

    # User registration and login
    path('api/register/', RegisterUser.as_view(), name='register'),
    path('api/login/', LoginUser.as_view(), name='login'),

    # JWT tokens
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Cart operations
    path('cart/', CartView.as_view(), name='cart'),
    path('cart/update/', UpdateCartQuantityView.as_view(), name='update-cart'),
    path('cart/delete/<int:cart_id>/', DeleteCartItemView.as_view(), name='delete-cart'),

    # Checkout product
    path('checkout/', CheckoutView.as_view(), name='checkout'),

    path('my-orders/', UserOrdersView.as_view()),
    path('cancel-order/<int:order_id>/', CancelOrderView.as_view()),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
