from django.urls import path
from django.views.generic import TemplateView

from product.views.product import CreateProductView, list_product, create_product
from product.views.variant import VariantView, VariantCreateView, VariantEditView

app_name = "product"

urlpatterns = [
    # Variants URLs
    path('variants/', VariantView.as_view(), name='variants'),
    path('variant/create', VariantCreateView.as_view(), name='create.variant'),
    path('variant/<int:id>/edit', VariantEditView.as_view(), name='update.variant'),

    # Products URLs
    path('create/', CreateProductView.as_view(), name='create.product'),
    path('list/', list_product, name='list.product'),
    path('check/', list_product, name='test'),
    path('create_product/', create_product, name='create_product')
]
