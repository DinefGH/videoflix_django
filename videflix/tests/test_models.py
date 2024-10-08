from django.test import TestCase
from django.contrib.auth import get_user_model
from videflix.models import Profile
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes

from videflix.tokens import account_activation_token


from django.utils import timezone
from videflix.models import LoginHistory



class UserProfileTestCase(TestCase):

    def setUp(self):
        self.User = get_user_model()

    def test_create_user_without_email(self):
        with self.assertRaises(ValueError) as context:
            self.User.objects.create_user(email=None, password='password123')
        self.assertEqual(str(context.exception), 'The Email field must be set')

    
    def test_create_superuser_without_is_staff(self):
        with self.assertRaises(ValueError) as context:
            self.User.objects.create_superuser(email='super@example.com', password='password123', is_staff=False)
        self.assertEqual(str(context.exception), 'Superuser must have is_staff=True.')

    def test_create_superuser_without_is_superuser(self):
        with self.assertRaises(ValueError) as context:
            self.User.objects.create_superuser(email='super@example.com', password='password123', is_superuser=False)
        self.assertEqual(str(context.exception), 'Superuser must have is_superuser=True.')

    def test_custom_user_str_method(self):
        user = self.User.objects.create_user(email='user@example.com', password='password123')
        self.assertEqual(str(user), 'user@example.com')

    def test_profile_str_method(self):
        user = self.User.objects.create_user(email='profileuser@example.com', password='password123')
        profile = Profile.objects.get(user=user)
        self.assertEqual(str(profile), 'profileuser@example.com')



class VerifyEmailAPITestCase(APITestCase):
    
    def setUp(self):
        # Create a user
        self.user = get_user_model().objects.create_user(
            email='testuser@example.com',
            password='password123',
            is_active=False  # User is inactive until email is verified
        )

    def test_email_verification_success(self):
        # Generate the token and uid
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = account_activation_token.make_token(self.user)
        
        # Build the verification URL
        url = reverse('email_verify', kwargs={'uidb64': uid, 'token': token})
        
        # Send GET request to verify email
        response = self.client.get(url)
        
        # Assert the response is successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Email verified successfully!")
        
        # Assert that the user's email is now verified (active)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)

    def test_email_verification_invalid_token(self):
        # Generate a valid uid but an invalid token
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        invalid_token = 'invalid-token'
        
        # Build the verification URL
        url = reverse('email_verify', kwargs={'uidb64': uid, 'token': invalid_token})
        
        # Send GET request with an invalid token
        response = self.client.get(url)
        
        # Assert the response is a 400 BAD REQUEST
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["message"], "Invalid or expired token.")
        
        # Assert the user is still inactive
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)

    def test_email_verification_invalid_uid(self):
        # Use an invalid uid but a valid token
        invalid_uid = urlsafe_base64_encode(force_bytes(999999))  # Non-existent user id
        token = account_activation_token.make_token(self.user)
        
        # Build the verification URL
        url = reverse('email_verify', kwargs={'uidb64': invalid_uid, 'token': token})
        
        # Send GET request with an invalid uid
        response = self.client.get(url)
        
        # Assert the response is a 400 BAD REQUEST
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["message"], "Invalid or expired token.")
        
        # Assert the user is still inactive
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)



class LoginHistoryModelTest(TestCase):
    
    def setUp(self):
        # Create a test user
        self.user = get_user_model().objects.create_user(
            email='testuser@example.com',
            password='password123'
        )

        # Login history data
        self.token = 'sample_token_value'
        self.ip_address = '127.0.0.1'
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'

        # Create a LoginHistory instance
        self.login_history = LoginHistory.objects.create(
            user=self.user,
            token=self.token,
            timestamp=timezone.now(),
            ip_address=self.ip_address,
            user_agent=self.user_agent
        )

    def test_login_history_creation(self):
        # Ensure the login history was created
        self.assertEqual(LoginHistory.objects.count(), 1)

    def test_login_history_fields(self):
        # Check if the fields are correctly stored
        self.assertEqual(self.login_history.user, self.user)
        self.assertEqual(self.login_history.token, self.token)
        self.assertEqual(self.login_history.ip_address, self.ip_address)
        self.assertEqual(self.login_history.user_agent, self.user_agent)
        self.assertIsInstance(self.login_history.timestamp, timezone.datetime)

    def test_string_representation(self):
        # Ensure the __str__ method returns the expected string
        expected_str = f"{self.user.email} - {self.login_history.timestamp}"
        self.assertEqual(str(self.login_history), expected_str)