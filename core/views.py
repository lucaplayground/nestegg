from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User


# Create your views here.
def index(request):
    return HttpResponse("Hello, world.")


def login_view(request):
    if request.method == 'POST':
        username_or_email = request.POST['username_or_email']
        password = request.POST['password']

        # Authenticate by username or email
        user = None
        if '@' in username_or_email:
            try:
                user = User.objects.get(email=username_or_email)
                username = user.username
            except User.DoesNotExist:
                username = None
        else:
            username = username_or_email

        if username:
            user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'core/login.html', {'error': 'Invalid credentials'})
    else:
        return render(request, 'core/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


def dashboard_view(request):
    return 'Hello World!'