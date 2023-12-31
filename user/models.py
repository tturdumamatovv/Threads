from django.db import models
from django.contrib.auth.models import PermissionsMixin, AbstractBaseUser, BaseUserManager
from rest_framework_simplejwt.tokens import RefreshToken
import random
import string
from django.utils import timezone
import os
from django.conf import settings


class UserManager(BaseUserManager):
    def create_user(self, email, username, password=None):
        if not email:
            raise ValueError('The email should be set!')

        email = self.normalize_email(email)
        user = self.model(email=email, username=username)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None):
        user = self.create_user(email, username, password)
        user.is_staff = True
        user.is_superuser = True
        user.is_verified = True
        user.save(using=self._db)
        return user

AUTH_PROVIDERS = { 'google': 'google','email': 'email'}

class CustomUser(PermissionsMixin, AbstractBaseUser):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    username = models.CharField(max_length=50, unique=True)
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.URLField(blank=True, null=True)
    link = models.URLField(blank=True, null=True)
    is_private = models.BooleanField(default=False)
    following = models.ManyToManyField('self', through='FollowingSystem', related_name='followers', symmetrical=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    auth_provider = models.CharField(max_length=255, blank=False, null=False, default=AUTH_PROVIDERS.get('email'))

    def is_profile_private(self):
        return self.is_private


    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email
    
    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }


class OTP(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    otp = models.CharField(max_length=4)
    created_at = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def generate_otp():
        digits = string.digits
        return ''.join(random.choice(digits) for i in range(4))

    @property
    def is_expired(self):
        time_threshold = timezone.now() - timezone.timedelta(minutes=5)
        return self.created_at < time_threshold


class FollowingSystem(models.Model):
    user_from = models.ForeignKey(CustomUser, related_name='rel_from_set', on_delete=models.CASCADE)
    user_to = models.ForeignKey(CustomUser, related_name='rel_to_set', on_delete=models.CASCADE)
    is_approved = models.BooleanField(default=False)
    is_pending = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return f'@{self.user_from.username} follows {self.user_to.username}'
