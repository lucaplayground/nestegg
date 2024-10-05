from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from .forms import LoginForm, CustomUserCreationForm, UserProfileForm, PasswordChangeForm


def LoginView(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                # print(f"User authenticated: {user}")  # Debug print
                auth_login(request, user)
                return redirect('dashboard')  # Redirect to dashboard
            else:
                # print("Authentication failed")  # Debug print
                form.add_error(None, 'Invalid username or password. Please try again.')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})


@login_required
def profile(request):
    if request.method == 'POST':
        if 'update_profile' in request.POST:
            form = UserProfileForm(request.POST, instance=request.user)
            if form.is_valid():
                form.save()
                messages.success(request, 'Your profile was successfully updated!')
                return redirect('profile')
        elif 'change_password' in request.POST:
            password_form = PasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)  # Important!
                messages.success(request, 'Your password was successfully updated!')
                return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user)
        password_form = PasswordChangeForm(request.user)
    
    return render(request, 'accounts/profile.html', {
        'form': form,
        'password_form': password_form
    })


def RegisterView(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('dashboard')  # Redirect to dashboard after successful registration
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})


def LogoutView(request):
    auth_logout(request)
    return redirect('login')  # Redirect to login page after logout


def AboutView(request):
    return render(request, 'about.html')