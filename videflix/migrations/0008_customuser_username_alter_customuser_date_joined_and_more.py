# Generated by Django 5.1 on 2024-10-01 09:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('videflix', '0007_video_video_file_1080p_video_video_file_360p_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='username',
            field=models.CharField(default='default_username', max_length=150, unique=True),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='date_joined',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='email',
            field=models.EmailField(max_length=254, unique=True, verbose_name='email address'),
        ),
    ]
