from django.urls import reverse
from django.views import generic
from django.shortcuts import get_object_or_404, redirect, render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from product.models import Variant, Product, ProductVariantPrice, ProductVariant, ProductImage
from django.db.models import Q
from product.utils import create_variants_list
from django.http import HttpResponse
from django.http import JsonResponse
import json
from django.db import transaction
from product.forms import ProductForm, ProductVariantForm, ProductVariantPriceForm


class CreateProductView(generic.TemplateView):
    template_name = 'products/create.html'

    def get_context_data(self, **kwargs):
        context = super(CreateProductView, self).get_context_data(**kwargs)
        variants = Variant.objects.filter(active=True).values('id', 'title')
        context['product'] = True
        context['variants'] = list(variants.all())
        return context

    def post(self, request, *args, **kwargs):
        # Parse JSON data from the request
        data = json.loads(request.body)

        # Extract product data
        product_name = data.get('productName')
        product_sku = data.get('productSKU')
        product_description = data.get('description')
        product_variants = data.get('productVariants')
        product_variant_prices = data.get('productVariantPrices')

        try:
            with transaction.atomic():
                # Save product
                product = Product.objects.create(
                    title=product_name,
                    sku=product_sku,
                    description=product_description
                )

                # Save product variants
                for item in product_variants:
                    variant_id = item['option']
                    tags = item['tags']
                    variant = Variant.objects.get(id=variant_id)

                    product_variants = [ProductVariant.objects.create(
                        variant_title=tag, variant=variant, product=product) for tag in tags]

                # Save product variant prices
                for item in product_variant_prices:
                    product_variants = [ProductVariant.objects.get(
                        variant_title=title, product=product) for title in item['title'].split('/') if title != '']

                    price = item['price']
                    stock = item['stock']
                    ProductVariantPrice.objects.create(
                        product_variant_one=product_variants[0],
                        product_variant_two=product_variants[1],
                        product_variant_three=product_variants[2],
                        price=price,
                        stock=stock,
                        product=product
                    )

        except Exception as e:
            error_message = str(e)
            print(error_message)
            return JsonResponse({'error': error_message}, status=500)
        else:
            return JsonResponse({'message': 'Product created successfully'}, status=200)


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
    paginator = Paginator(products, min(len(products), 2))
    page_number = request.GET.get('page')

    try:
        products = paginator.page(page_number)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    return render(request, 'products/list.html', {'products': products, 'variants': variants})


def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product_form = ProductForm(request.POST or None, instance=product)

    if request.method == 'POST':
        if product_form.is_valid():
            product_form.save()
            # product_variant_form.save()
            return redirect(list_product(request))

    return render(request, 'products/edit.html', {'product_form': product_form})
