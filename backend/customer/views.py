from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework import status
from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from .models import Customer,Address
from orders.models import Order
from products.models import Product
from products.views import get_wishlist_products
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
@api_view(['GET'])
def get_customer_profile(request):
    customer_id = request.GET.get('customer_id')
    if not customer_id:
        return JsonResponse({"error": "Customer ID is required"}, status=400)
    
    # Retrieve the customer object (associated with the User model)
    customer = get_object_or_404(Customer, customer_id=customer_id)
    
    # Fetch all orders where order_status is 'Delivered'
    previous_orders = Order.objects.filter(customer_id=customer_id, order_status="Delivered")
    
    customer_data = {
        "customer_id": customer.customer_id,
        "name": customer.user.username,
        "email": customer.email,
        "phone_no": customer.phone_no,
        "address": {
            "location": customer.address.location if customer.address else None,
            "city": customer.address.city if customer.address else None,
            "state": customer.address.state if customer.address else None,
            "postal_code": customer.address.pincode if customer.address else None,
        },
        "previous_orders": [],
        "wishlist": get_wishlist_products(customer_id),
    }

    # Iterate through the previous orders and collect the related product information
    for order in previous_orders:
        product = Product.objects.get(product_id=order.product_id.product_id)  # Use product_id from the order
        product_info = {
            "product_id": product.product_id,
            "name": product.product_name,
            "description": product.product_description,
            "price": product.product_price,
            "image": product.product_images,
            "quantity": order.quantity,
            "status": order.order_status
        }
        customer_data["previous_orders"].append(product_info)
    
    return JsonResponse(customer_data)

@csrf_exempt
@api_view(['POST'])
def login_customer(request):
    username = request.data.get('username')
    password = request.data.get('password')

    # Authenticate the user using the User model (not Customer model anymore)
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

    # Log the received data (optional for debugging)
    print(f"Username: {username}")
    print(f"Password: {password}")
    print(f"Phone Number: {phone_no}")
    
    if Customer.objects.filter(phone_no=phone_no).exists():
        return JsonResponse({"error": "Phone Number already in use"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Create a new user with the provided credentials
        user = User.objects.create_user(username=username, password=password,first_name=username)

        # Create a new customer entry linked to this user
        customer = Customer(
            user=user,
            phone_no=phone_no,
            address=None  # Set to None or a default address if desired
        )
        customer.save()
        return JsonResponse({"message": f"Customer created successfully. Welcome, {username}!"}, status=status.HTTP_201_CREATED)
    except ValidationError as e:
        print(f"Validation Error: {e}")  # Log specific validation errors
        return JsonResponse({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print(f"Exception occurred: {e}")  # Log any other exceptions
        return JsonResponse({"error": "An error occurred during signup."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@csrf_exempt
@api_view(['POST'])
def logout_customer(request):
    # Log out the user
    logout(request)
    return JsonResponse({
        'message': 'Logout successful'
    }, status=status.HTTP_200_OK)

@csrf_exempt
@api_view(['POST'])
def add_address(request):
    customer_id = request.data.get('customer')
    pincode = request.data.get('pincode')
    city = request.data.get('city')
    state = request.data.get('state')
    location = request.data.get('location')
    landmark = request.data.get('landmark')

    print(f"Location: {location}")
    print(f"City: {city}")
    print(f"State: {state}")
    print(f"Pincode: {pincode}")
    print(f"Landmark: {landmark}")
    print(f"Customer ID: {customer_id}")

    try:
        # Create the address object
        address = Address(
            pincode=pincode,
            city=city,
            state=state,
            location=location,
            landmark=landmark
        )
        address.save()  # Save the address to the database

        # Retrieve the customer based on the provided customer_id
        customer = get_object_or_404(Customer, customer_id=customer_id)

        # Assign the created address to the customer
        customer.address = address  # Set the address field of the customer

        # Save the customer to update the address_id in the Customer table
        customer.save()

        return JsonResponse({"message": f"Address saved successfully and linked to customer."}, status=status.HTTP_201_CREATED)
    except ValidationError as e:
        print(f"Validation Error: {e}")  # Log specific validation errors
        return JsonResponse({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print(f"Exception occurred: {e}")  # Log any other exceptions
        return JsonResponse({"error": "An error occurred during adding address."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
@api_view(['DELETE'])
def delete_address(request):
    customer_id = request.data.get('customer')
    address_id = request.data.get('address_id')  # The address ID to delete

    try:
        # Get the address to delete based on the address_id and customer_id
        address = get_object_or_404(Address, address_id=address_id, customer_id=customer_id)

        # Delete the address
        address.delete()

        return JsonResponse({"message": "Address deleted successfully"}, status=status.HTTP_200_OK)
    except Exception as e:
        return JsonResponse({"error": "An error occurred while deleting the address"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['PUT'])
def update_address(request):
    customer_id = request.data.get('customer')
    address_id = request.data.get('address_id')

    # Get the fields to update from the request
    fields_to_update = ['pincode', 'city', 'state', 'location', 'landmark']
    
    try:
        # Retrieve the address object to update
        address = get_object_or_404(Address, address_id=address_id, customer_id=customer_id)
        
        # Update the fields that are provided in the request
        for field in fields_to_update:
            value = request.data.get(field)
            if value:
                setattr(address, field, value)
        
        address.save()  # Save the updated address

        return JsonResponse({"message": "Address updated successfully"}, status=status.HTTP_200_OK)
    
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


