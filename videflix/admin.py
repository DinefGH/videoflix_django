from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Profile
from django.utils.translation import gettext_lazy as _
from rest_framework.authtoken.models import Token
from .models import LoginHistory
from .models import Video
from import_export import resources
from import_export.admin import ImportExportModelAdmin

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('email','is_staff', 'is_active', 'date_joined')
    list_filter = ('is_staff', 'is_active', 'is_superuser')

    fieldsets = (
        (None, {'fields': ('email','password')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email','password1', 'password2', 'is_staff', 'is_active'),
        }),
    )

    exclude = ('date_joined',)

    search_fields = ('email',)
    ordering = ('email',)

admin.site.register(CustomUser, CustomUserAdmin)

class ProfileAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    """
    Customizes the admin interface for the Profile model.
    
    Features:
        - list_display: Displays user, bio, location, and birth_date in the admin list view.
        - search_fields: Enables searching by the user's email and location.
    """
    list_display = ('user', 'bio', 'location', 'birth_date')
    search_fields = ('user__email', 'location')

admin.site.register(Profile, ProfileAdmin)


class TokenAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    """
    Customizes the admin interface for the Token model.
    
    Features:
        - list_display: Displays token key, user, and creation date in the admin list view.
    """
    list_display = ['key', 'user', 'created']

admin.site.register(Token, TokenAdmin)


class LoginHistoryAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    """
    Customizes the admin interface for the LoginHistory model.
    
    Features:
        - list_display: Displays user, timestamp, IP address, and user agent in the admin list view.
        - list_filter: Filters login history by user and timestamp.
    """
    list_display = ['user', 'timestamp', 'ip_address', 'user_agent']
    list_filter = ['user', 'timestamp']

admin.site.register(LoginHistory, LoginHistoryAdmin)



class VideoAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    """
    Customizes the admin interface for the Video model.
    
    Features:
        - list_display: Displays title, created_at, and description in the admin list view.
        - search_fields: Enables searching by video title.
        - list_filter: Filters videos by their creation date.
    """
    list_display = ('title', 'created_at', 'description')  
    search_fields = ('title',)  
    list_filter = ('created_at',)  

admin.site.register(Video, VideoAdmin)


class VideoResource(resources.ModelResource):
    """
    Defines the resource class for importing and exporting Video model data.
    """
    class Meta:
        model = Video  

