from django.contrib import admin
from django.apps import apps

# Register your models here.

app_name = 'product'

# Get all models from the specified app
app_models = apps.get_app_config(app_name).get_models()

# Iterate through all models
for model in app_models:
    # Create a dynamic admin class
    class DynamicModelAdmin(admin.ModelAdmin):
        # Generate a list of field names dynamically
        list_display = [field.name for field in model._meta.fields]

    # Register the dynamic admin class with the model
    admin.site.register(model, DynamicModelAdmin)
