from django.urls import path
from .views import CategoryListView,CategoryDetailView

app_name = 'product'

urlpatterns = [
    path('',CategoryListView.as_view(), name='categories_list'),
    path('<slug>/',CategoryDetailView.as_view(), name='categories_detail')
]
