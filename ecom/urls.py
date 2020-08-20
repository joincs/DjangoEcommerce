"""ecom URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from carts.views import (
    CartView,
    ItemCountView,
    CheckoutView,
    CheckoutFinalView
    )
from orders.views import (
    AddressSelectFormView,
    UserAddressCreateView,
    OrderListView,OrderDetail
    )

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include("product.urls",namespace='products') ),
    path('categories/', include("product.urls_categories", namespace='product_categories') ),
    path('cart/',CartView.as_view(),name='cart'),
    path('orders/<int:pk>',OrderDetail.as_view(),name='orders_detail'),
    path('cart/count/',ItemCountView.as_view(),name='item_count'),
    path('checkout/',CheckoutView.as_view(),name='checkout'),
    path('checkout/address/',AddressSelectFormView.as_view(),name='order_address'),
    path('checkout/address/add',UserAddressCreateView.as_view(),name='user_address_create'),
    path('checkout/final/',CheckoutFinalView.as_view(),name='checkout_final'),
    path('accounts/', include('allauth.urls')),



]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
