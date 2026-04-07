from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser
from django.db import models

class UserManager(BaseUserManager):
    def create_user(self,email,password,nickname,**kwargs):
        if not email:
            raise ValueError
        user = self.model(
            email=self.normalize_email(email),
            nickname = nickname,
            **kwargs,
        )
        user.set_password(password)
        user.save(using = self._db)
        return user

    def create_superuser(self,email,password,nickname,**kwargs):
        user = self.create_user(email,password,nickname,**kwargs)
        user.is_admin = True
        user.is_superuser = True
        user.save(using = self._db)
        return user

class User(AbstractBaseUser):
    nickname = models.CharField(max_length=50,unique=True)
    email = models.EmailField(max_length=255, unique=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nickname']

    class Meta:
        verbose_name = "Users"
        verbose_name_plural = "Users"
