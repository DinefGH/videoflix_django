from datetime import date
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

from django.contrib.auth.models import BaseUserManager
from django.utils import timezone

from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.crypto import get_random_string




class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password=password, **extra_fields)



class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_('email address'), unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'  # Use email as the unique identifier
    REQUIRED_FIELDS = []  # No additional fields required

    def __str__(self):
        return self.email



class Profile(models.Model):
    """
    User profile linked to the CustomUser model.

    Fields:
        - user: One-to-one relationship with CustomUser.
        - bio: A short biography for the user.
        - location: User's location.
        - birth_date: User's birth date.
    
    Methods:
        - __str__: Returns the email of the linked user.
    """
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)  # Link Profile to CustomUser
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=30, blank=True)
    birth_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.user.email 
    
class LoginHistory(models.Model):
    """
    Stores login history for users, including token, IP address, and user agent.

    Fields:
        - user: ForeignKey to CustomUser, linking the history to the user.
        - token: The authentication token used during login.
        - timestamp: When the login occurred.
        - ip_address: The IP address from which the user logged in.
        - user_agent: The user agent string from the login session.
    
    Methods:
        - __str__: Returns the email of the user and the timestamp of the login.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    token = models.CharField(max_length=255)  # Store the token used
    timestamp = models.DateTimeField(default=timezone.now)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.email} - {self.timestamp}"
    


class Video(models.Model):
    """
    Video model representing uploaded videos and their transcoded versions.

    Fields:
        - title: The title of the video.
        - description: A brief description of the video.
        - video_file: The original video file.
        - video_file_360p: 360p resolution version of the video.
        - video_file_480p: 480p resolution version of the video.
        - video_file_720p: 720p resolution version of the video.
        - video_file_1080p: 1080p resolution version of the video.
        - thumbnail: A thumbnail image for the video.
        - category: The category the video belongs to.
        - created_at: The timestamp when the video was uploaded.
    
    Methods:
        - __str__: Returns the title of the video.
    """
    title = models.CharField(max_length=100)
    description = models.TextField()
    video_file = models.FileField(upload_to='videos/', default='videos/default_video.mp4')
    video_file_360p = models.FileField(upload_to='videos/', null=True, blank=True)
    video_file_480p = models.FileField(upload_to='videos/', null=True, blank=True)
    video_file_720p = models.FileField(upload_to='videos/', null=True, blank=True)
    video_file_1080p = models.FileField(upload_to='videos/', null=True, blank=True)
    thumbnail = models.ImageField(upload_to='thumbnails/', null=True, blank=True)
    category = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.title