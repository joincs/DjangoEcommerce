from django.urls import path
from .views import home,ProductDetailView, ProductListView, VariationListView

app_name = 'product'

urlpatterns = [
    path('',home, name='home'),
    path('product/',ProductListView.as_view(), name='product_list'),
    path("<int:pk>/",ProductDetailView.as_view(),name='product_detail'),
    path("<int:pk>/inventory/",VariationListView.as_view(),name='product_inventory'),
    
]
