from django.forms import forms, ModelForm, CharField, TextInput, Textarea, BooleanField, CheckboxInput

from product.models import Variant, Product, ProductVariant, ProductVariantPrice


class VariantForm(ModelForm):
    class Meta:
        model = Variant
        fields = '__all__'
        widgets = {
            'title': TextInput(attrs={'class': 'form-control'}),
            'description': Textarea(attrs={'class': 'form-control'}),
            'active': CheckboxInput(attrs={'class': 'form-check-input', 'id': 'active'})
        }


class FormClassMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.fields:
            field = self.fields[field_name]
            field.widget.attrs['placeholder'] = field.label
            field.widget.attrs.setdefault('class', 'form-control')


class ProductForm(FormClassMixin, ModelForm):
    class Meta:
        model = Product
        fields = ['title', 'sku', 'description']
        widgets = {'class': 'form-control'}


class ProductVariantForm(FormClassMixin, ModelForm):
    class Meta:
        model = ProductVariant
        fields = ['variant_title', 'variant', 'product']


class ProductVariantPriceForm(FormClassMixin, ModelForm):
    class Meta:
        model = ProductVariantPrice
        fields = ['price', 'stock', 'product']
