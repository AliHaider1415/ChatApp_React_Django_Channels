from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import UserProfile
import json, time
from django.db.models import Q
from .consumers import AsyncConsumer
import base64, os
from django.conf import settings

# API for logging in using JWT Custom Authentication

@csrf_exempt
def login_token(request):
    try:
        phone_number = request.POST['phone_number']
        password = request.POST['password']

        User = get_user_model()

        try:
            user_profile = UserProfile.objects.get(phone_number=phone_number)
            user = user_profile.user
            
        except UserProfile.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)

        # Check the password
        if user.check_password(password):
            refresh = RefreshToken.for_user(user)
            
            # Add custom claims
            refresh['user_id'] = user.id
            refresh['username'] = user.username

            access_token = str(refresh.access_token)

            response_data = {
                'user_id': user.id,
                'username': user.username,
                'phone_number': phone_number,
                'access_token': access_token,
                'refresh_token': str(refresh),
                'message': 'Login successful',
            }
            
            request.session['user_id'] = user.id
            request.session['username'] = user.username

            return JsonResponse(response_data)
        else:
            return JsonResponse({'error': 'Invalid credentials'}, status=401)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
    

def update_user_status(user_id, new_status):
    record = UserProfile.objects.get(user_id=user_id)
    record.status = new_status
    record.save()
    # return UserProfile.objects.filter(user_id=user_id).update(status=status)
    print(f"New Status {record.status}")

@csrf_exempt
def logout_token(request):
    # AsyncConsumer.disconnect(self, close_code=1000)
    user_id = request.POST['user_id']
    print(f"ID: {user_id}")

    update_user_status(user_id, 'offline')
    response_data = {"message": "Successfully logged out"}  # Create a dictionary
    return JsonResponse(response_data)


# API for Registration
@csrf_exempt
def sign_up(request):
    try:
        username = request.POST['username']
        phone_number = request.POST['phone_number']
        password = request.POST['password']
        email = request.POST['email']

        # Check if a user with the provided phone number or email already exists
        if UserProfile.objects.filter(phone_number=phone_number).exists() or get_user_model().objects.filter(email=email).exists():
            return JsonResponse({'error': 'User with this phone number or email already exists'}, status=400)

        # Create a new user without date_of_birth
        user = get_user_model().objects.create_user(username=username, email=email, password=password)

        # Create a UserProfile for the user with optional fields
        UserProfile.objects.create(user=user, phone_number=phone_number, date_of_birth=None)  # You can set other optional fields to None

        response_data = {
            'user_id': user.id,
            'username': user.username,
            'phone_number': phone_number,
            'message': 'User has been successfully registered',
        }

        return JsonResponse(response_data)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
    


@api_view(['GET'])
def get_contacts(request):
    query_param = request.query_params.get('username', None)
    
    if query_param:
        # Filter users based on username query parameter
        users = User.objects.filter(Q(username__icontains=query_param))
    else:
        # Get all users
        users = User.objects.all()
        
    # Retrieve user data with status from UserProfile model
    user_data = [{'id': user.id, 
                  'username': user.username, 
                  'status': user.userprofile.status if hasattr(user, 'userprofile') else 'Offline'} 
                  for user in users]
    
    return Response(user_data)

@csrf_exempt
@api_view(['POST'])
def upload_file(request):
    if request.method == 'POST':
        file_data = request.FILES.get('fileData')
        if file_data:
            try:
                upload_dir = settings.MEDIA_ROOT  # Use MEDIA_ROOT from settings.py

                # Save the file to the specified directory
                file_path = os.path.join(upload_dir, file_data.name)
                with open(file_path, 'wb') as f:
                    for chunk in file_data.chunks():
                        f.write(chunk)

                file_url = request.build_absolute_uri(settings.MEDIA_URL + file_data.name)

                return JsonResponse({'fileURL': file_url,
                                     'fileSize' : file_data.size }, status=201)
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=400)
        else:
            return JsonResponse({'error': 'No file data provided'}, status=400)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)