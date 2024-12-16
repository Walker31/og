from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework import status
from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from .models import Customer, Address
from orders.models import Order
from products.views import get_wishlist_products
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
@api_view(['GET'])
def get_customer_profile(request):
    customer_id = request.GET.get('customer_id')
    if not customer_id:
        return JsonResponse({"error": "Customer ID is required"}, status=400)
    
    # Retrieve the customer object
    customer = get_object_or_404(Customer, customer_id=customer_id)
    
    # Fetch all delivered orders for the customer
    delivered_orders = Order.objects.filter(customer_id=customer_id, order_status="Delivered")
    
    # Prepare the customer data
    customer_data = {
        "customer_id": customer.customer_id,
        "name": customer.user.username,
        "email": customer.email,
        "phone_no": customer.phone_no,
        "updated_at": customer.updated_at,
        "created_at":customer.created_at,
        "previous_orders": [],
        "wishlist": get_wishlist_products(customer_id),
    }

    # Collect order details for delivered orders
    for order in delivered_orders:
        order_items = order.order_items.all()  
        for item in order_items:
            product = item.product
            product_info = {
                "product_id": product.product_id,
                "name": product.product_name,
                "description": product.product_description,
                "price": product.product_price,
                "image": product.product_images,
                "quantity": item.quantity,
                "status": order.order_status,
            }
            customer_data["previous_orders"].append(product_info)

    return JsonResponse(customer_data, safe=False)

@csrf_exempt
@api_view(['POST'])
def login_customer(request):
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        customer = Customer.objects.filter(user=user).first()
        return JsonResponse({
            'message': 'Login successful',
            'customer_id': customer.customer_id,
            'username': user.username,
            'email': user.email
        }, status=status.HTTP_200_OK)
    else:
        return JsonResponse({
            'error': 'Invalid username or password'
        }, status=status.HTTP_401_UNAUTHORIZED)

@csrf_exempt
@api_view(['POST'])
def signup_customer(request):
    username = request.data.get('username')
    password = request.data.get('password')
    phone_no = request.data.get('phone_no')

    if Customer.objects.filter(phone_no=phone_no).exists():
        return JsonResponse({"error": "Phone Number already in use"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.create_user(username=username, password=password, first_name=username)
        customer = Customer(user=user, phone_no=phone_no)
        customer.save()
        return JsonResponse({"message": f"Customer created successfully. Welcome, {username}!"}, status=status.HTTP_201_CREATED)
    except ValidationError as e:
        return JsonResponse({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return JsonResponse({"error": "An error occurred during signup."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
@api_view(['POST'])
def logout_customer(request):
    logout(request)
    return JsonResponse({'message': 'Logout successful'}, status=status.HTTP_200_OK)

@csrf_exempt
@api_view(['POST'])
def add_address(request):
    customer_id = request.data.get('customer')
    pincode = request.data.get('pincode')
    city = request.data.get('city')
    state = request.data.get('state')
    location = request.data.get('location')
    landmark = request.data.get('landmark')

    try:
        customer = get_object_or_404(Customer, customer_id=customer_id)

        # Create and save the address for the customer
        address = Address(customer=customer, pincode=pincode, city=city, state=state, location=location, landmark=landmark)
        address.save()

        return JsonResponse({"message": "Address saved successfully and linked to customer."}, status=status.HTTP_201_CREATED)
    except ValidationError as e:
        return JsonResponse({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return JsonResponse({"error": "An error occurred during adding address."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
@api_view(['DELETE'])
def delete_address(request):
    customer_id = request.data.get('customer')
    address_id = request.data.get('address_id')  

    try:
        address = get_object_or_404(Address, address_id=address_id, customer_id=customer_id)
        address.delete()

        return JsonResponse({"message": "Address deleted successfully"}, status=status.HTTP_200_OK)
    except Exception as e:
        return JsonResponse({"error": "An error occurred while deleting the address"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_addresses_by_customer(request):
    customer_id = request.query_params.get('customer_id')

    if not customer_id:
        return JsonResponse({"error": "Customer ID is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        customer = Customer.objects.get(customer_id=customer_id)
        addresses = customer.addresses.all()

        if addresses.exists():
            from .serializers import AddressSerializer
            serialized_addresses = AddressSerializer(addresses, many=True)
            return JsonResponse(serialized_addresses.data, status=status.HTTP_200_OK,safe=False)
        else:
            return JsonResponse({"error": "No addresses found for this customer"}, status=status.HTTP_404_NOT_FOUND)
    
    except Customer.DoesNotExist:
        return JsonResponse({"error": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)

@csrf_exempt
@api_view(['PUT'])
def update_address(request):
    customer_id = request.data.get('customer')
    address_id = request.data.get('address_id')

    fields_to_update = ['pincode', 'city', 'state', 'location', 'landmark']
    
    try:
        address = get_object_or_404(Address, address_id=address_id, customer_id=customer_id)
        
        # Update the fields that are provided in the request
        for field in fields_to_update:
            value = request.data.get(field)
            if value:
                setattr(address, field, value)
        
        address.save()

        return JsonResponse({"message": "Address updated successfully"}, status=status.HTTP_200_OK)
    
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
