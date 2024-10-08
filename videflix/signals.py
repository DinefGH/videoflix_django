import os
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import CustomUser, Profile, Video
from videflix.tasks import convert_360p, convert_480p, convert_720p, convert_1080p
from django.db.models.signals import post_save
from django.conf import settings








@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Signal to create a Profile when a new CustomUser is created.

    Args:
        sender (model class): The model class sending the signal (CustomUser).
        instance (CustomUser): The instance of the user being created.
        created (bool): Boolean indicating if the instance is newly created.
    """
    if created:
        Profile.objects.create(user=instance)



@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    """
    Signal to save the Profile whenever the CustomUser is saved.

    Args:
        sender (model class): The model class sending the signal (CustomUser).
        instance (CustomUser): The instance of the user being saved.
    """
    instance.profile.save()


@receiver(post_save, sender=Video)
def video_post_save(sender, instance, created, **kwargs):
    """
    Signal triggered after a Video is saved, which converts and saves the video to different resolutions.

    Args:
        sender (model class): The model class sending the signal (Video).
        instance (Video): The instance of the video being saved.
        created (bool): Boolean indicating if the instance is newly created.
    
    Conversion details:
    - Converts the original video into 360p, 480p, 720p, and 1080p resolutions.
    - Updates the Video instance with the paths of the converted files.
    """
    print('Video saved')
    if created:
        print('New video created')
        video_path = instance.video_file.path
        base, ext = os.path.splitext(video_path)
        
        video_360p_path = convert_360p(video_path)
        video_480p_path = convert_480p(video_path)
        video_720p_path = convert_720p(video_path)
        video_1080p_path = convert_1080p(video_path)
    
        if video_360p_path:
            instance.video_file_360p.name = os.path.relpath(video_360p_path, settings.MEDIA_ROOT)
        if video_480p_path:
            instance.video_file_480p.name = os.path.relpath(video_480p_path, settings.MEDIA_ROOT)
        if video_720p_path:
            instance.video_file_720p.name = os.path.relpath(video_720p_path, settings.MEDIA_ROOT)
        if video_1080p_path:
            instance.video_file_1080p.name = os.path.relpath(video_1080p_path, settings.MEDIA_ROOT)
    
        instance.save()


@receiver(post_delete, sender=Video)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes the original video file and all transcoded versions when a Video instance is deleted.

    Args:
        sender (model class): The model class sending the signal (Video).
        instance (Video): The instance of the video being deleted.
    """
    if instance.video_file:
        if os.path.isfile(instance.video_file.path):
            os.remove(instance.video_file.path)

    base, ext = os.path.splitext(instance.video_file.path)
    
    resolutions = ["360p", "480p", "720p", "1080p"]
    
    for res in resolutions:
        transcoded_file = f"{base}_{res}{ext}"
        if os.path.isfile(transcoded_file):
            os.remove(transcoded_file)