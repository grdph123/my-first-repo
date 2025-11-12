from django.shortcuts import render
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.models import User
import json
from django.contrib.auth import logout as auth_logout
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

# Decorator untuk handle CORS
def handle_cors(view_func):
    @csrf_exempt
    def wrapped_view(request, *args, **kwargs):
        # Handle preflight OPTIONS request
        if request.method == 'OPTIONS':
            response = JsonResponse({"status": True})
            response["Access-Control-Allow-Origin"] = "http://10.0.2.2"
            response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
            response["Access-Control-Allow-Headers"] = "Content-Type, X-CSRFToken"
            response["Access-Control-Allow-Credentials"] = "true"
            response["Access-Control-Max-Age"] = "86400"
            return response
        return view_func(request, *args, **kwargs)
    return wrapped_view

@handle_cors
def logout(request):
    username = request.user.username
    try:
        auth_logout(request)
        response = JsonResponse({
            "username": username,
            "status": True,
            "message": "Logged out successfully!"
        }, status=200)
        response["Access-Control-Allow-Origin"] = "http://10.0.2.2"
        response["Access-Control-Allow-Credentials"] = "true"
        return response
    except:
        response = JsonResponse({
            "status": False,
            "message": "Logout failed."
        }, status=401)
        response["Access-Control-Allow-Origin"] = "http://10.0.2.2"
        response["Access-Control-Allow-Credentials"] = "true"
        return response

@handle_cors
def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                auth_login(request, user)
                response = JsonResponse({
                    "username": user.username,
                    "status": True,
                    "message": "Login successful!"
                }, status=200)
                response["Access-Control-Allow-Origin"] = "http://10.0.2.2"
                response["Access-Control-Allow-Credentials"] = "true"
                return response
            else:
                response = JsonResponse({
                    "status": False,
                    "message": "Login failed, account is disabled."
                }, status=401)
                response["Access-Control-Allow-Origin"] = "http://10.0.2.2"
                response["Access-Control-Allow-Credentials"] = "true"
                return response
        else:
            response = JsonResponse({
                "status": False,
                "message": "Login failed, please check your username or password."
            }, status=401)
            response["Access-Control-Allow-Origin"] = "http://10.0.2.2"
            response["Access-Control-Allow-Credentials"] = "true"
            return response
    else:
        response = JsonResponse({
            "status": False,
            "message": "Invalid request method."
        }, status=400)
        response["Access-Control-Allow-Origin"] = "http://10.0.2.2"
        response["Access-Control-Allow-Credentials"] = "true"
        return response

@handle_cors
def register(request):
    if request.method == 'POST':
        print(f"Content-Type: {request.content_type}")
        print(f"POST data: {dict(request.POST)}")
        print(f"Body: {request.body}")
        
        username = None
        password1 = None
        password2 = None
        
        # Handle JSON data dari Flutter (pbp_django_auth)
        if request.content_type == 'application/json':
            try:
                data = json.loads(request.body)
                username = data.get('username')
                password1 = data.get('password1')
                password2 = data.get('password2')
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}")
                response = JsonResponse({
                    "status": False,
                    "message": "Invalid JSON format."
                }, status=400)
                response["Access-Control-Allow-Origin"] = "http://10.0.2.2"
                response["Access-Control-Allow-Credentials"] = "true"
                return response
        # Handle form data
        elif request.content_type == 'application/x-www-form-urlencoded':
            username = request.POST.get('username')
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')
        else:
            # Default - try to get from POST anyway
            username = request.POST.get('username')
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')

        # Check if all fields are provided
        if not username or not password1 or not password2:
            print(f"Missing fields - username: {username}, pass1: {password1}, pass2: {password2}")
            response = JsonResponse({
                "status": False,
                "message": "All fields are required."
            }, status=400)
            response["Access-Control-Allow-Origin"] = "http://10.0.2.2"
            response["Access-Control-Allow-Credentials"] = "true"
            return response

        # Check if the passwords match
        if password1 != password2:
            response = JsonResponse({
                "status": False,
                "message": "Passwords do not match."
            }, status=400)
            response["Access-Control-Allow-Origin"] = "http://10.0.2.2"
            response["Access-Control-Allow-Credentials"] = "true"
            return response
        
        # Check if the username is already taken
        if User.objects.filter(username=username).exists():
            response = JsonResponse({
                "status": False,
                "message": "Username already exists."
            }, status=400)
            response["Access-Control-Allow-Origin"] = "http://10.0.2.2"
            response["Access-Control-Allow-Credentials"] = "true"
            return response
        
        # Create the new user
        user = User.objects.create_user(username=username, password=password1)
        user.save()
        
        # RESPONSE: Ubah 'success' menjadi True untuk konsisten dengan Flutter code
        response = JsonResponse({
            "username": user.username,
            "status": "success",  # Tetap string 'success' sesuai Flutter code
            "message": "User created successfully!"
        }, status=200)
        response["Access-Control-Allow-Origin"] = "http://10.0.2.2"
        response["Access-Control-Allow-Credentials"] = "true"
        return response
    
    else:
        response = JsonResponse({
            "status": False,
            "message": "Invalid request method."
        }, status=400)
        response["Access-Control-Allow-Origin"] = "http://10.0.2.2"
        response["Access-Control-Allow-Credentials"] = "true"
        return response