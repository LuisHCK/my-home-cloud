from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver


def upload_avatar_handler(instance, filename):
    """Upload file in custom storage"""
    extension = filename.split('.')[-1]
    random_uuid = uuid4()
    random_name = "{}.{}".format(random_uuid, random_name)
    return "./storage/avatars/{filename}".format(
        filename=random_name
    )


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=30, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    avatar = models.FileField(upload_to=upload_avatar_handler, max_length=255)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
