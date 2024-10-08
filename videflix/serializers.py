from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Video

class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration, handles creating a new user with an email and password.

    Fields:
        - email: The user's email address (required).
        - password: The user's password (write-only, required).
    """
    password = serializers.CharField(write_only=True)

    class Meta:
        model = get_user_model()
        fields = ['email', 'password']

    def create(self, validated_data):
        """
        Create a new user with the provided email and password.
        
        Args:
            validated_data (dict): Contains the validated user data.
        
        Returns:
            user (CustomUser): The created user instance.
        """
        user = get_user_model().objects.create_user(
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user
    

class VideoSerializer(serializers.ModelSerializer):
    """
    Serializer for Video objects, handles serialization of video metadata and files.

    Fields:
        - id: The unique identifier for the video.
        - title: The title of the video.
        - description: A brief description of the video.
        - video_file: The original video file.
        - video_file_360p: The 360p version of the video.
        - video_file_480p: The 480p version of the video.
        - video_file_720p: The 720p version of the video.
        - video_file_1080p: The 1080p version of the video.
        - thumbnail: A thumbnail image for the video.
        - category: The category to which the video belongs.
        - created_at: The date and time when the video was uploaded.
    """
    thumbnail = serializers.ImageField(max_length=None, use_url=True)
    video_file = serializers.FileField(max_length=None, use_url=True)

    class Meta:
        model = Video
        fields = [
            'id',
            'title',
            'description',
            'video_file',
            'video_file_360p',
            'video_file_480p',
            'video_file_720p',
            'video_file_1080p',
            'thumbnail',
            'category',
            'created_at',
        ]