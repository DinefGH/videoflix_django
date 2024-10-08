from django.test import TestCase
from unittest.mock import patch
from videflix.models import CustomUser, Profile
from django.test import TestCase
from unittest.mock import patch
from videflix.models import Video
import os
from django.test import TestCase
from unittest.mock import patch
from videflix.models import Video
import os




class UserProfileSignalTest(TestCase):
    def test_create_user_profile(self):
        # Create a CustomUser instance (only using email, no username)
        user = CustomUser.objects.create(email='testuser@example.com')
        
        # Assert that a profile is created when a user is created
        self.assertTrue(Profile.objects.filter(user=user).exists())

    @patch('videflix.models.Profile.save')
    def test_save_user_profile(self, mock_save):
        # Create a CustomUser instance (using email, not username)
        user = CustomUser.objects.create(email='testuser@example.com')

        # Save the user to trigger the save_user_profile signal
        user.save()

        # Assert that the profile save method is called
        self.assertTrue(mock_save.called)





class VideoSignalTest(TestCase):
    @patch('videflix.signals.convert_360p')
    @patch('videflix.signals.convert_480p')
    @patch('videflix.signals.convert_720p')
    @patch('videflix.signals.convert_1080p')
    def test_video_post_save(self, mock_convert_1080p, mock_convert_720p, mock_convert_480p, mock_convert_360p):
        # Mock the conversion function results
        mock_convert_360p.return_value = '/path/to/video_360p.mp4'
        mock_convert_480p.return_value = '/path/to/video_480p.mp4'
        mock_convert_720p.return_value = '/path/to/video_720p.mp4'
        mock_convert_1080p.return_value = '/path/to/video_1080p.mp4'

        # Create a Video instance
        video = Video.objects.create(title="Test Video", video_file='original_video.mp4')

        # Assert that the conversion functions are called
        mock_convert_360p.assert_called_once_with(video.video_file.path)
        mock_convert_480p.assert_called_once_with(video.video_file.path)
        mock_convert_720p.assert_called_once_with(video.video_file.path)
        mock_convert_1080p.assert_called_once_with(video.video_file.path)

        # Assert that the video file paths were updated
        self.assertEqual(video.video_file_360p.name, os.path.relpath('/path/to/video_360p.mp4', 'media/'))
        self.assertEqual(video.video_file_480p.name, os.path.relpath('/path/to/video_480p.mp4', 'media/'))
        self.assertEqual(video.video_file_720p.name, os.path.relpath('/path/to/video_720p.mp4', 'media/'))
        self.assertEqual(video.video_file_1080p.name, os.path.relpath('/path/to/video_1080p.mp4', 'media/'))





class VideoDeleteSignalTest(TestCase):
    @patch('os.remove')  # Mock os.remove to avoid actual file deletion
    def test_auto_delete_file_on_delete(self, mock_remove):
        # Create a Video instance
        video = Video.objects.create(title="Test Video", video_file='original_video.mp4')

        # Define the mock behavior of os.path.isfile to always return True
        with patch('os.path.isfile', return_value=True):
            # Delete the video to trigger the post_delete signal
            video.delete()

            # Assert that os.remove is called for each file (original + resolutions)
            base, ext = os.path.splitext(video.video_file.path)
            mock_remove.assert_any_call(video.video_file.path)  # Original file
            mock_remove.assert_any_call(f"{base}_360p{ext}")
            mock_remove.assert_any_call(f"{base}_480p{ext}")
            mock_remove.assert_any_call(f"{base}_720p{ext}")
            mock_remove.assert_any_call(f"{base}_1080p{ext}")

            # Ensure os.remove was called exactly 5 times (one for each file)
            self.assertEqual(mock_remove.call_count, 5)
