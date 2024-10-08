from django.contrib import admin
from django.urls import include, path
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from videoflixbackend import settings
from videflix.views import UserRegistrationView
from videflix.views import VerifyEmailView
from videflix.views import LoginView, CSRFTokenView, LogoutView
from videflix.views import PasswordResetRequestView, PasswordResetConfirmView
from django.conf import settings
from django.conf.urls.static import static
from debug_toolbar.toolbar import debug_toolbar_urls
from videflix.views import VideosByCategoryView, VideoDetailView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('verify-email/<uidb64>/<token>/', VerifyEmailView.as_view(), name='email_verify'),
    path('login/', LoginView.as_view(), name='login'),
    path('csrf/', CSRFTokenView.as_view(), name='csrf'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('reset-password/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('api/videos-by-category/', VideosByCategoryView.as_view(), name='videos-by-category'),
    path('api/videos/<int:pk>/', VideoDetailView.as_view(), name='video-detail'),

]+ staticfiles_urlpatterns()
urlpatterns +=  debug_toolbar_urls()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

