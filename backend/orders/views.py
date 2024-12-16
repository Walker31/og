from rest_framework.decorators import api_view
from .models import Order, OrderItem
from customer.models import Customer,Address
from products.models import Product
from django.http import JsonResponse
from rest_framework import status
from django.db import transaction

@api_view(['POST'])
def place_order(request):
    data = request.data

    # Validate required field
    required_fields = ['customer_id', 'items', 'address_id', 'order_total', 'order_status', 'payment_type']
    for field in required_fields:
        if field not in data:
            return JsonResponse({'error': f'{field} is required'}, status=status.HTTP_400_BAD_REQUEST)

    # Validate customer
    try:
        customer = Customer.objects.get(customer_id=data['customer_id'])
    except Customer.DoesNotExist:
        return JsonResponse({'error': 'Invalid customer_id'}, status=status.HTTP_400_BAD_REQUEST)

    # Validate address
    try:
        address = Address.objects.get(id=data['address_id'])
    except Address.DoesNotExist:
        return JsonResponse({'error': 'Invalid address_id'}, status=status.HTTP_400_BAD_REQUEST)

    # Validate items
    items = data['items']  # List of products and quantities
    if not isinstance(items, list) or not items:
        return JsonResponse({'error': 'Items must be a non-empty list'}, status=status.HTTP_400_BAD_REQUEST)

    with transaction.atomic():
        # Create the Order
        new_order = Order.objects.create(
            customer_id=customer,
            address_id=address,
            order_total=data['order_total'],
            order_status=data['order_status'],
            payment_type=data['payment_type'],
        )

        # Create OrderItems
        for item in items:
            try:
                product = Product.objects.get(product_id=item['product_id'])
            except Product.DoesNotExist:
                return JsonResponse({'error': f'Invalid product_id: {item["product_id"]}'}, status=status.HTTP_400_BAD_REQUEST)

            quantity = item.get('quantity', 1)
            if quantity < 1:
                return JsonResponse({'error': 'Quantity must be at least 1'}, status=status.HTTP_400_BAD_REQUEST)

            OrderItem.objects.create(
                order=new_order,
                product_id=product,
                quantity=quantity
            )

    return JsonResponse({'order_id': new_order.order_id}, status=status.HTTP_201_CREATED)
