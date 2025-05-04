from django.urls import path
from .views import get_product_options

urlpatterns = [
    path('api/products/<int:product_id>/options/', get_product_options, name='product-options'),
]