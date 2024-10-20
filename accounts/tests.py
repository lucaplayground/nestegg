from django.test import TestCase
import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from .forms import CustomUserCreationForm, LoginForm, UserProfileForm, CustomPasswordChangeForm
from .models import CustomUser
import re
from django.db import IntegrityError



# Create your tests here.

User = get_user_model()


# Model Tests
@pytest.mark.django_db
class TestCustomUserModel:
    '''Test the CustomUser model'''
    def test_create_user(self):
        user = User.objects.create_user(username='testuser', email='test@example.com', password='testpass123')
        assert user.username == 'testuser'
        assert user.email == 'test@example.com'
        assert user.default_currency == 'USD'

    def test_default_currency(self):
        user = User.objects.create_user(username='testuser', email='test@example.com', password='testpass123', default_currency='CNY')
        assert user.default_currency == 'CNY'
    
    def test_unique_email(self):
        User.objects.create_user(username='user1', email='test@example.com', password='password123')
        with pytest.raises(IntegrityError):
            User.objects.create_user(username='user2', email='test@example.com', password='password456')


# Form Tests
@pytest.mark.django_db
class TestForms:
    '''Test the forms'''
    def test_custom_user_creation_form(self):
        form = CustomUserCreationForm(data={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'default_currency': 'USD'
        })
        assert form.is_valid()

    def test_login_form(self):
        form = LoginForm(data={
            'username': 'testuser',
            'password': 'testpass123'
        })
        assert form.is_valid()


# View Tests
@pytest.mark.django_db
class TestViews:
    '''Test the views'''
    def test_home_view_redirect(self, client):
        response = client.get(reverse('home'))
        assert response.status_code == 302

    def test_login_view(self, client):
        response = client.get(reverse('login'))
        assert response.status_code == 200
        assert 'form' in response.context

    def test_register_view(self, client):
        response = client.get(reverse('register'))
        assert response.status_code == 200
        assert 'form' in response.context

    def test_profile_view(self, client, django_user_model):
        user = django_user_model.objects.create_user(username='testuser', password='12345')
        client.login(username='testuser', password='12345')
        response = client.get(reverse('profile'))
        assert response.status_code == 200
        assert 'form' in response.context
        assert 'password_form' in response.context

    def test_logout_view(self, client, django_user_model):
        user = django_user_model.objects.create_user(username='testuser', password='12345')
        client.login(username='testuser', password='12345')
        response = client.get(reverse('logout'))
        assert response.status_code == 302


# Authentication Tests
@pytest.mark.django_db
class TestAuthentication:
    '''Test the authentication'''
    def test_login_correct_credentials(self, client):
        User.objects.create_user(username='testuser', password='12345')
        response = client.post(reverse('login'), {'username': 'testuser', 'password': '12345'})
        assert response.status_code == 302
        assert response.url == reverse('dashboard')

    def test_login_incorrect_credentials(self, client):
        response = client.post(reverse('login'), {'username': 'wronguser', 'password': 'wrongpass'})
        assert response.status_code == 200
        assert 'form' in response.context
        assert response.context['form'].errors

    def test_register_user(self, client):
        response = client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'default_currency': 'USD'
        })
        assert response.status_code == 302
        assert User.objects.filter(username='newuser').exists()


# Security Tests
@pytest.mark.django_db
class TestSecurity:
    def test_csrf_protection(self, client):
        response = client.get(reverse('login'))
        assert 'csrftoken' in response.cookies
        
        # Check if CSRF token is in the HTML
        content = response.content.decode('utf-8')
        assert 'csrfmiddlewaretoken' in content

    def test_csrf_token_required(self, client):
        # Get the login page to retrieve the CSRF token
        response = client.get(reverse('login'))
        csrftoken = response.cookies['csrftoken'].value

        # Attempt a POST request with an invalid CSRF token
        response = client.post(reverse('login'), 
                               {'username': 'testuser', 'password': '12345', 'csrfmiddlewaretoken': 'invalid_token'},
                               HTTP_X_CSRFTOKEN='invalid_token')
        
        # This login should fail
        assert 'form' in response.context
        assert response.context['form'].errors

    def test_valid_csrf_token_accepted(self, client):
        # Get the login page to retrieve the CSRF token
        response = client.get(reverse('login'))
        csrftoken = response.cookies['csrftoken'].value

        # Attempt a POST request with a valid CSRF token
        response = client.post(reverse('login'), 
                               {'username': 'testuser', 'password': '12345'},
                               HTTP_X_CSRFTOKEN=csrftoken)
        
        # The login should process normally
        assert response.status_code == 200
        assert 'form' in response.context
