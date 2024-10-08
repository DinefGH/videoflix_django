from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from django.core import mail
from rest_framework.authtoken.models import Token
from django.test import TestCase
from rest_framework.test import APIClient
from videflix.models import CustomUser, LoginHistory
from rest_framework.test import APITestCase
from videflix.models import Video
from django.urls import reverse
from rest_framework.test import APITestCase
from videflix.models import Video
from django.urls import reverse
from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from rest_framework.test import APITestCase
from django.urls import reverse
from django.core import mail
from django.contrib.auth.models import User
from unittest.mock import patch








User = get_user_model()

class UserRegistrationAPITestCase(APITestCase):

    def test_user_registration(self):
        url = reverse('register') 
        print(f"Resolved URL: {url}")

        data = {
            "email": "testuser@example.com",
            "password": "password123"
        }

        response = self.client.post(url, data, format='json')

        # Assert the response is successful
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["message"], "User registered successfully! Please check your email to verify your account.")

        # Assert that the user was created and is inactive
        User = get_user_model()
        user = User.objects.get(email="testuser@example.com")
        self.assertFalse(user.is_active)  # The user should be inactive until email verification

        # Check that an email was sent
        self.assertEqual(len(mail.outbox), 1)  # Ensure one email was sent
        self.assertIn("Verify your email address", mail.outbox[0].subject)  # Check subject

    def test_registration_with_invalid_email(self):
        url = reverse('register')
        data = {
            "email": "invalidemail",  # Invalid email format
            "password": "password123"
        }
    
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)  # Ensure 'email' error is returned

    def test_registration_with_missing_password(self):
        url = reverse('register')
        data = {
            "email": "validemail@example.com",
            "password": ""  # Missing password
        }
    
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)  # Ensure 'password' error is returned


from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from django.test import TestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from videflix.models import LoginHistory

class LoginViewTest(TestCase):

    def setUp(self):
        # Set up test data
        self.client = APIClient()
        self.email = 'testuser@example.com'  # Assign the email to self.email
        self.password = 'password123'
        self.user = get_user_model().objects.create_user(
            email=self.email,
            password=self.password
        )
        self.login_url = reverse('login')  # Ensure this is the name of your login view's URL

    def test_login_success_with_custom_ip(self):
        # Simulate a login with a valid IP address in the X-Forwarded-For header
        data = {
            'email': self.email,
            'password': self.password
        }
        headers = {
            'HTTP_X_FORWARDED_FOR': '203.0.113.195',  # Simulate a custom IP address
            'HTTP_USER_AGENT': 'Mozilla/5.0'  # Simulate a User-Agent
        }
        
        response = self.client.post(self.login_url, data, format='json', **headers)

        # Check if the login was successful
        self.assertEqual(response.status_code, 200)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['message'], "Login successful")

        # Verify the LoginHistory was created with the correct IP and user agent
        login_history = LoginHistory.objects.get(user=self.user)
        self.assertEqual(login_history.ip_address, '203.0.113.195')  # Ensure the IP is correctly extracted
        self.assertEqual(login_history.user_agent, 'Mozilla/5.0')

    def test_login_failure(self):
        # Test an unsuccessful login (invalid password)
        data = {
            'email': self.email,
            'password': 'wrongpassword'
        }

        response = self.client.post(self.login_url, data, format='json')

        # Check if the login failed
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], "Invalid credentials")

        # Ensure no token or login history was created
        self.assertFalse(Token.objects.filter(user=self.user).exists())
        self.assertFalse(LoginHistory.objects.filter(user=self.user).exists())

    def test_login_invalid_credentials(self):
        # Test with invalid credentials
        data = {
            "email": self.email,  # Corrected self.email
            "password": 'wrongpassword'
        }
        
        response = self.client.post(self.login_url, data, format='json')

        # Check that the response indicates failure (HTTP 400 Bad Request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Verify that the error message is as expected
        self.assertEqual(response.data['error'], 'Invalid credentials')







class LogoutViewTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='testuser@example.com',
            password='password123'
        )
        self.token = Token.objects.create(user=self.user)
        self.logout_url = reverse('logout')

        response = self.client.post(self.logout_url)

        self.assertEqual(response.status_code, 200)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['message'], "Logged out successfully")

        self.assertFalse(Token.objects.filter(key=self.token.key).exists())

        self.assertEqual(response.cookies['auth_token'].value, '')


class CSRFTokenViewTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.csrf_url = reverse('csrf')  # Ensure this is the correct name for your URL

    def test_csrf_token_set(self):
        # Send a GET request to the CSRF token view
        response = self.client.get(self.csrf_url)

        # Check if the response contains the correct message
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['message'], 'CSRF cookie set')

        # Check if the CSRF cookie is set in the response
        self.assertIn('csrftoken', response.cookies)

        # Optionally, check if the CSRF cookie is correctly set (not HttpOnly)
        csrf_cookie = response.cookies['csrftoken']
        self.assertFalse(csrf_cookie.get('httponly')) 




class PasswordResetRequestViewTest(APITestCase):
    def setUp(self):
        # Create a CustomUser instance
        self.user = CustomUser.objects.create_user(email='testuser@example.com', password='testpassword')
        self.url = reverse('password_reset_request')  # Use the actual URL name

    def test_password_reset_request_no_email(self):
        response = self.client.post(self.url, data={})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error'], 'Email is required')

    def test_password_reset_request_non_existent_email(self):
        response = self.client.post(self.url, data={'email': 'nonexistent@example.com'})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data['error'], 'User with this email does not exist')



class PasswordResetConfirmViewTest(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(email='testuser@example.com', password='testpassword')
        self.token = default_token_generator.make_token(self.user)
        self.uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))  # No need for .decode()
        self.url = reverse('password_reset_confirm', kwargs={'uidb64': self.uidb64, 'token': self.token})

    def test_password_reset_invalid_user(self):
        invalid_uidb64 = urlsafe_base64_encode(force_bytes(999))  # Simulating an invalid user
        url = reverse('password_reset_confirm', kwargs={'uidb64': invalid_uidb64, 'token': self.token})
        response = self.client.post(url, data={'password': 'newpassword', 'confirm_password': 'newpassword'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error'], 'Invalid user')

    def test_password_reset_invalid_token(self):
        url = reverse('password_reset_confirm', kwargs={'uidb64': self.uidb64, 'token': 'invalid-token'})
        response = self.client.post(url, data={'password': 'newpassword', 'confirm_password': 'newpassword'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error'], 'Invalid token')

    def test_password_reset_passwords_do_not_match(self):
        response = self.client.post(self.url, data={'password': 'newpassword', 'confirm_password': 'differentpassword'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error'], 'Passwords do not match')

    def test_password_reset_successful(self):
        response = self.client.post(self.url, data={'password': 'newpassword', 'confirm_password': 'newpassword'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['message'], 'Password reset successful')
        
        # Ensure the password was updated
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpassword'))



class VideosByCategoryViewTest(APITestCase):
    def setUp(self):
        # Create some videos with categories
        Video.objects.create(title="Video 1", category="Category 1")
        Video.objects.create(title="Video 2", category="Category 2")
        Video.objects.create(title="Video 3", category="Category 1")
        self.url = reverse('videos-by-category')  # Update with your actual URL name

    def test_get_videos_by_category(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Category 1', [d['category'] for d in response.data])
        self.assertIn('Category 2', [d['category'] for d in response.data])
        self.assertEqual(len(response.data[0]['videos']), 2)


class VideoDetailViewTest(APITestCase):
    def setUp(self):
        self.video = Video.objects.create(title="Test Video", category="Test Category")
        self.url = reverse('video-detail', kwargs={'pk': self.video.pk})

    def test_get_video_detail_success(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['title'], 'Test Video')

    def test_get_video_detail_not_found(self):
        url = reverse('video-detail', kwargs={'pk': 9999})  # Non-existent video
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data['error'], 'Video not found')