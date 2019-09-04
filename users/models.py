from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
import uuid
import json

class Comment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(blank=True)


class House(models.Model):
    '''
    House Object. has unique id served as primary key. The creator (User) is nullable.
    '''
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    url = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    owner_name = models.TextField(max_length=20)
    contact = models.TextField(max_length=20)
    created_date = timezone.now()
    state = models.TextField(max_length=20)
    city = models.TextField(max_length=20)
    address = models.TextField(max_length=100)
    postal = models.TextField(max_length=5)
    lat = models.DecimalField(max_digits=22, decimal_places=16, null=True, blank=True)
    lon = models.DecimalField(max_digits=22, decimal_places=16, null=True, blank=True)
    name = models.TextField(max_length=100, blank=True)
    beds = models.TextField(max_length=10)
    baths = models.TextField(max_length=10)
    rent = models.DecimalField(decimal_places=2, max_digits=9, blank=True)
    deposit = models.DecimalField(decimal_places=2, max_digits=9, blank=True)
    unit = models.TextField(blank=True)
    lease_length = models.TextField(max_length=20, blank=True)
    available = models.TextField(max_length=20, blank=True)
    desciption = models.TextField(blank=True)
    Amenities = models.TextField(blank=True)
    comments = models.ManyToManyField(Comment)

class Profile(models.Model):
    '''
    User Profile. One user will only has one profile
    '''
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='static/pictures/UserPhoto/',
                               default='static/pictures/UserPhoto/default-user.png')
    bio = models.TextField(max_length=500, blank=True)
    website = models.URLField(default='', blank=True)
    address = models.CharField(max_length=50, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    favorites = models.ManyToManyField(House)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    '''
    Create user profile if user is created
    '''
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    '''
    Save user profile if there is any changes
    '''
    instance.profile.save()

class trial(models.Model):
    '''
    Used to test the connection between Django and Scrapy
    '''
    name = models.TextField()

