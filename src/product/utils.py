from .models import ProductVariant, Variant


def create_variants_list():
    variants = {variant.title: [value[0] for value in ProductVariant.objects.filter(
        variant=variant).distinct().values_list('variant_title')] for variant in Variant.objects.all()}
    return variants
