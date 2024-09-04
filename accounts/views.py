from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate
from django.shortcuts import redirect, render
from .serializers import UserSerializer


# Uses auth_login to create a session for the user
def LoginView(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('home')  # Redirect to dashboard
        else:
            return render(request, 'accounts/login.html', {'error': 'Invalid credentials'})
    return render(request, 'accounts/login.html')


# A class-based view for the registration page
def RegisterView(request):
    if request.method == 'POST':
        serializer = UserSerializer(data=request.POST)
        if serializer.is_valid():
            user = serializer.save()
            if user:
                auth_login(request, user)
                return redirect('home')  # Redirect to dashboard after successful registration
        return render(request, 'accounts/register.html', {'errors': serializer.errors})
    return render(request, 'accounts/register.html')


# Uses auth_logout to destroy the session for the user
def LogoutView(request):
    auth_logout(request)
    return redirect('login')  # Redirect to login page after logout