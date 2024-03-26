from django.views import generic
from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from product.models import Variant, Product, ProductVariantPrice
from django.db.models import Q
from product.utils import create_variants_list


class CreateProductView(generic.TemplateView):
    template_name = 'products/create.html'

    def get_context_data(self, **kwargs):
        context = super(CreateProductView, self).get_context_data(**kwargs)
        variants = Variant.objects.filter(active=True).values('id', 'title')
        context['product'] = True
        context['variants'] = list(variants.all())
        return context


def list_product(request):
    # Getting filter parameters
    title = request.GET.get('title')
    price_from = request.GET.get('price_from')
    price_to = request.GET.get('price_to')
    variant = request.GET.get('variant')
    date = request.GET.get('date')

    variants = create_variants_list()

    # Building query for dynamically fetching products
    product_query = Q()
    if title:
        product_query &= Q(**{'title__icontains': title})

    if date:
        product_query &= Q(**{'created_at__date': date})

    filtered_products = Product.objects.filter(product_query)

    products = []
    # Creating list of dictionaries for products
    for product in filtered_products:

        # Building query for price filter for each product variant price
        product_variant_query = Q()
        if price_from:
            product_variant_query &= Q(
                **{'price__gte': price_from})

        if price_to:
            product_variant_query &= Q(
                **{'price__lte': price_to})

        if variant:
            product_variant_query &= (
                Q(**{'product_variant_one__variant_title': variant}) |
                Q(**{'product_variant_two__variant_title': variant}) |
                Q(**{'product_variant_three__variant_title': variant})
            )

        product_variant_prices = ProductVariantPrice.objects.filter(
            product=product).filter(product_variant_query)

        # if no product variants meet the parameters skip this product
        if not product_variant_prices.exists():
            continue

        product = product.__dict__
        product['variants'] = product_variant_prices
        products.append(product)

    # Pagination
    paginator = Paginator(products, min(len(products), 6))
    page_number = request.GET.get('page')

    try:
        products = paginator.page(page_number)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    return render(request, 'products/list.html', {'products': products, 'variants': variants})
