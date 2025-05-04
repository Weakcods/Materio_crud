from django.shortcuts import render
from django.http import JsonResponse
from .models import Product, ProductOption, ProductOptionChoice

def get_product_options(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
        options = []
        
        for option in product.options.all():
            choices = option.choices.filter(is_available=True).values(
                'id', 'name', 'additional_price'
            )
            if choices:
                options.append({
                    'name': option.name,
                    'is_required': option.is_required,
                    'choices': list(choices)
                })
        
        return JsonResponse(options, safe=False)
    except Product.DoesNotExist:
        return JsonResponse({'error': 'Product not found'}, status=404)
