from django.views import generic
from django.shortcuts import render
import logging

from product.models import Variant, Product, ProductVariantPrice


class CreateProductView(generic.TemplateView):
    template_name = 'products/create.html'

    def get_context_data(self, **kwargs):
        context = super(CreateProductView, self).get_context_data(**kwargs)
        variants = Variant.objects.filter(active=True).values('id', 'title')
        context['product'] = True
        context['variants'] = list(variants.all())
        return context


def list_product(request):
    products = []
    for product in Product.objects.all():
        product_variant_prices = ProductVariantPrice.objects.filter(
            product=product)
        product = product.__dict__
        product['variants'] = product_variant_prices
        products.append(product)

    return render(request, 'products/list.html', {'products': products})
