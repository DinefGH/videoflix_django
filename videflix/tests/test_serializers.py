from django.test import TestCase
from django.contrib.auth import get_user_model
from videflix.serializers import UserRegistrationSerializer

class UserRegistrationSerializerTest(TestCase):

    def setUp(self):
        self.User = get_user_model()

    def test_valid_user_registration(self):
        # Test with valid data
        valid_data = {
            "email": "testuser@example.com",
            "password": "password123"
        }
        
        # Create a serializer instance with valid data
        serializer = UserRegistrationSerializer(data=valid_data)

        # Check if the serializer data is valid
        self.assertTrue(serializer.is_valid())

        # Save the serializer to create the user
        user = serializer.save()

        # Check if the user was created and is in the database
        self.assertTrue(self.User.objects.filter(email="testuser@example.com").exists())

        # Verify the password is hashed and not stored in plain text
        self.assertTrue(user.check_password("password123"))

    def test_missing_email(self):
        # Test with missing email
        invalid_data = {
            "email": "",  # Empty email
            "password": "password123"
        }

        serializer = UserRegistrationSerializer(data=invalid_data)

        # Serializer should be invalid due to missing email
        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)

    def test_missing_password(self):
        # Test with missing password
        invalid_data = {
            "email": "testuser@example.com",
            "password": ""  # Empty password
        }

        serializer = UserRegistrationSerializer(data=invalid_data)

        # Serializer should be invalid due to missing password
        self.assertFalse(serializer.is_valid())
        self.assertIn("password", serializer.errors)

    def test_invalid_email_format(self):
        # Test with invalid email format
        invalid_data = {
            "email": "invalidemail",  # Invalid email format
            "password": "password123"
        }

        serializer = UserRegistrationSerializer(data=invalid_data)

        # Serializer should be invalid due to invalid email
        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)
