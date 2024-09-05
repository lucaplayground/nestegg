from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate
from django.shortcuts import redirect, render
from .forms import LoginForm, CustomUserCreationForm


def LoginView(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                auth_login(request, user)
                return redirect('home')  # Redirect to dashboard
        else:
            form.add_error(None, 'Invalid credentials')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})


def RegisterView(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('home')  # Redirect to dashboard after successful registration
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})


def LogoutView(request):
    auth_logout(request)
    return redirect('login')  # Redirect to login page after logout