import logging
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from .tokens import account_activation_token
from django.conf import settings
from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import UserRegistrationSerializer
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth import get_user_model
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.contrib.auth import authenticate
from django.http import JsonResponse
from rest_framework.authtoken.models import Token
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from .models import LoginHistory
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.views.decorators.cache import cache_page
from .models import Video
from .serializers import VideoSerializer
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken







CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)

logger = logging.getLogger('password_reset')



User = get_user_model()

logger = logging.getLogger(__name__)

class UserRegistrationView(APIView):
    """
    Handles user registration by creating a new user and sending a verification email.
    """

    def post(self, request):
        """
        Registers a new user.

        Validates the request data, saves the new user as inactive, and sends a verification email.
        If the data is invalid, returns a 400 Bad Request with error details.

        Returns:
            Response: 201 Created on success, 400 Bad Request on failure.
        """
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.is_active = False
            user.save()

            self.send_verification_email(user, request)
            return Response({"message": "User registered successfully! Please check your email to verify your account."}, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def send_verification_email(self, user, request):
        """
        Sends an email verification to the newly registered user.
        """
        try:
            logger.info(f"Preparing to send verification email to {user.email}")
            
            # The logic for sending the email remains unchanged
            token = account_activation_token.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))

            current_site = get_current_site(request)
            verification_link = reverse('email_verify', kwargs={'uidb64': uid, 'token': token})

            verification_url = f"http://{current_site.domain}{verification_link}"

            subject = 'Verify your email address'
            context = {
                'user': user,
                'verification_url': verification_url
            }

            html_content = render_to_string('emails/verification_email.html', context)
            text_content = f"Dear {user.email},\nPlease click the link below to verify your email:\n{verification_url}"

            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email],
            )
            email.attach_alternative(html_content, "text/html")
            email.send()
            
            logger.info(f"Verification email successfully sent to {user.email}")
        
        except Exception as e:
            logger.error(f"Error sending verification email to {user.email}: {e}")
            raise


class VerifyEmailView(APIView):

    def get(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist) as e:
            logger.error(f"Failed to decode UID or user not found: {e}")
            return Response({"message": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)

        if user is not None and account_activation_token.check_token(user, token):
            user.is_active = True 
            user.save()
            return Response({"message": "Email verified successfully!"}, status=status.HTTP_200_OK)
        else:
            logger.warning(f"Invalid token for user {uid}")
            return Response({"message": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(ensure_csrf_cookie, name='dispatch')  # Ensure CSRF token is set
class LoginView(APIView):
    """
    Authenticates a user and generates an access and refresh JWT token.
    """

    def get_client_ip(self, request):
        """
        Retrieves the client's IP address from the request object.
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            # In case of multiple IP addresses, take the first one
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def post(self, request):
        # Get email and password from the request data
        email = request.data.get("email")
        password = request.data.get("password")

        # Log the login attempt
        logger.info(f"Login attempt for email: {email}")

        # Check if email or password is missing
        if not email or not password:
            logger.warning("Email or password missing in login request.")
            return Response({"error": "Email and password are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Authenticate the user
        user = authenticate(request, username=email, password=password)

        # If authentication fails, return an error response
        if user is None:
            logger.warning(f"Authentication failed for email: {email}")
            return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)

        # If authentication is successful, generate JWT tokens
        refresh = RefreshToken.for_user(user)

        logger.info(f"Login successful for user: {user.email}")

        # Log the login history
        LoginHistory.objects.create(
            user=user,
            token=str(refresh.access_token),
            ip_address=self.get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )

        # Return access and refresh tokens in the response
        response = Response(
            {
                "message": "Login successful",
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            },
            status=status.HTTP_200_OK
        )

        # Optionally set the access token as an HttpOnly cookie
        response.set_cookie(
            key='jwt_access_token',
            value=str(refresh.access_token),
            httponly=True,
            secure=True,  # Set to False if not using HTTPS in development
            samesite='Lax'
        )

        return response


class RefreshTokenView(TokenRefreshView):
    """
    Handles refreshing of JWT access tokens.
    """
    pass


class LogoutView(APIView):
    """
    Logs out the user by blacklisting the refresh token.
    """

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh_token")
            token = RefreshToken(refresh_token)
            # Blacklist the refresh token
            token.blacklist()
            return Response({"message": "Logged out successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    
    



@method_decorator(ensure_csrf_cookie, name='dispatch')
class CSRFTokenView(APIView):
    """
    Provides the CSRF token required for state-changing requests.

    This view sets the CSRF token as a cookie and responds with a message.
    """
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        """
        Sends a CSRF token in a cookie.

        Args:
            request: The incoming request.

        Returns:
            Response: 200 OK when the CSRF token is successfully set.
        """
        return Response({'message': 'CSRF cookie set'})
    



class PasswordResetRequestView(APIView):
    """
    Handles password reset requests by sending a reset email.

    This view generates a password reset token and sends it to the user via email.
    """
    def post(self, request):
        """
        Generates a password reset token and sends it via email.

        Args:
            request: The incoming request with the user's email.

        Returns:
            Response: 200 OK if email is sent, 404 Not Found if the user doesn't exist, or 500 Internal Server Error if there's an issue.
        """
        logger.debug("Password reset request received.")
        
        email = request.data.get('email')
        if email is None:
            logger.warning("Password reset requested without an email.")
            return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            logger.warning(f"Password reset requested for non-existent email: {email}")
            return Response({'error': 'User with this email does not exist'}, status=status.HTTP_404_NOT_FOUND)
        
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        
        logger.info(f"Password reset token generated for user {user.email}")
        
        reset_url = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}"
        
        email_body = render_to_string('emails/password_reset_email.html', {
            'user': user,
            'reset_url': reset_url,
        })
        
        try:
            send_mail(
                subject='Password Reset Request',
                message=email_body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                html_message=email_body
            )
            logger.info(f"Password reset email sent to {user.email}")
        except Exception as e:
            logger.error(f"Error sending password reset email to {user.email}: {str(e)}")
            return Response({'error': 'Error sending password reset email'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({'message': 'Password reset email sent'}, status=status.HTTP_200_OK)
    

    

class PasswordResetConfirmView(APIView):
    """
    Resets the user's password after verifying the token.

    This view allows the user to reset their password by providing a valid token and new password.
    """
    def post(self, request, uidb64, token):
        """
        Resets the user's password if the token is valid.

        Args:
            uidb64: Base64-encoded user ID.
            token: Token used for password reset.
            request: The request containing the new password.

        Returns:
            Response: 200 OK on success, 400 Bad Request if token or data is invalid.
        """
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({'error': 'Invalid user'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not default_token_generator.check_token(user, token):
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)
        
        password = request.data.get('password')
        confirm_password = request.data.get('confirm_password')

        if not password or password != confirm_password:
            return Response({'error': 'Passwords do not match'}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(password)
        user.save()

        return Response({'message': 'Password reset successful'}, status=status.HTTP_200_OK)
    

class VideosByCategoryView(APIView):
    """
    Lists all videos, grouped by category.

    This view returns videos categorized under different categories.
    """
    def get(self, request):
        """
        Fetches videos grouped by their category.

        Args:
            request: The incoming request.

        Returns:
            Response: 200 OK with the list of categories and their respective videos.
        """
        categories = Video.objects.values_list('category', flat=True).distinct()
        data = []

        for category in categories:
            videos = Video.objects.filter(category=category)
            serializer = VideoSerializer(videos, many=True, context={'request': request})

            data.append({
                'category': category,
                'videos': serializer.data
            })

        return Response(data)

class VideoDetailView(APIView):
    """
    Provides details of a single video.

    This view returns all details related to a specific video.
    """
    def get(self, request, pk):
        """
        Fetches details of a specific video by its primary key.

        Args:
            pk: The primary key of the video.

        Returns:
            Response: 200 OK if the video is found, 404 Not Found if the video doesn't exist.
        """
        try:
            video = Video.objects.get(pk=pk)
            serializer = VideoSerializer(video, context={'request': request})
            return Response(serializer.data)
        except Video.DoesNotExist:
            return Response({'error': 'Video not found'}, status=404)