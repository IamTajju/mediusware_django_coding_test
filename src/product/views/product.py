from django.views import generic
from django.shortcuts import render
import logging

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

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

    paginator = Paginator(products, 2)
    page_number = request.GET.get('page')

    try:
        products = paginator.page(page_number)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        products = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        products = paginator.page(paginator.num_pages)

    return render(request, 'products/list.html', {'products': products})
