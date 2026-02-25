from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from myapp.views import (
    AdminLoginView, AdminOrderListView, CancelOrderView, CheckoutView, ProductViewSet, CartView, UpdateCartQuantityView, DeleteCartItemView,
    RegisterUser, LoginUser, ProductImageUploadView, DeleteProductImagesView, UserOrdersView,
    ContactView, ContactDeleteView,
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.conf import settings
from django.conf.urls.static import static

router = DefaultRouter()
router.register(r'product', ProductViewSet)  # प्रॉडक्टसाठी CRUD endpoints auto-create होतात
from myapp.views import create_admin_secure
urlpatterns = [
    path('create-admin-secure/', create_admin_secure),
    path('admin/', admin.site.urls),  # Django admin panel साठी

    path('', include(router.urls)),  # ProductViewSet साठी default CRUD endpoints

    # Admin login
    path('api/admin-login/', AdminLoginView.as_view()),  # admin लॉगिन API
    path('api/admin/orders/', AdminOrderListView.as_view()),  # admin ला सर्व orders बघण्यासाठी

    # Product images
    path('upload-images/', ProductImageUploadView.as_view(), name='upload-images'),  # प्रॉडक्ट इमेज अपलोड करण्यासाठी
    path('delete-product-images/<int:product_id>/', DeleteProductImagesView.as_view(), name='delete_product_images'),  # प्रॉडक्टच्या इमेजेस delete करण्यासाठी

    # User registration and login
    path('api/register/', RegisterUser.as_view(), name='register'),  # नवीन user रजिस्ट्रेशनसाठी
    path('api/login/', LoginUser.as_view(), name='login'),  # user login करण्यासाठी

    # JWT tokens
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # JWT token generate करण्यासाठी
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # JWT token refresh करण्यासाठी

    # Cart operations
    path('cart/', CartView.as_view(), name='cart'),  # cart मध्ये item add / बघण्यासाठी
    path('cart/update/', UpdateCartQuantityView.as_view(), name='update-cart'),  # cart मध्ये quantity update करण्यासाठी
    path('cart/delete/<int:cart_id>/', DeleteCartItemView.as_view(), name='delete-cart'),  # cart मधून item delete करण्यासाठी

    # Checkout product
    path('checkout/', CheckoutView.as_view(), name='checkout'),  # checkout साठी

    # User orders
    path('my-orders/', UserOrdersView.as_view()),  # user चे स्वतःचे orders बघण्यासाठी
    path('cancel-order/<int:order_id>/', CancelOrderView.as_view()),  # order cancel करण्यासाठी

    # ✅ Contact APIs
    path('contact/', ContactView.as_view(), name='contact'),  # contact form डेटा send करण्यासाठी (POST)
    path('contact/<int:pk>/', ContactDeleteView.as_view(), name='delete-contact'),  # contact डेटा delete करण्यासाठी (DELETE)
]

# Debug mode मध्ये media files serve करण्यासाठी
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
