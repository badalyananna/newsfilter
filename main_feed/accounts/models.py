from django.db import models
from datetime import datetime
import pytz
# Create your models here.
from django.contrib.auth.models import (BaseUserManager, AbstractBaseUser)

class UserManager(BaseUserManager):
    def create_user(self, email, first_name, password=None): # here we pass only required fields
        if not email:
            raise ValueError('Users must have an email address')
        email=self.normalize_email(email)
        user = self.model(email=email, first_name=first_name)
        user.set_password(password)
        user.last_upd = datetime.now(pytz.timezone('UTC'))
        user.save(using=self._db)
        return user

    def create_staffuser(self, email, first_name, password=None): # here we pass only required fields
        user = self.create_user(email, first_name, password=password)
        user.staff = True
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, password=None): # here we pass only required fields
        user = self.create_user(email, first_name, password=password)
        user.staff = True
        user.admin = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser):
    username = None
    email = models.EmailField(verbose_name='email address', max_length=255, unique=True)
    first_name = models.CharField(verbose_name='first name', max_length=30)
    last_name = models.CharField(verbose_name='last name', max_length=30)
    last_upd = models.DateTimeField(blank=True, null=True)

    is_active = models.BooleanField(default=True)
    staff = models.BooleanField(default=False) # a admin user; non super-user
    admin = models.BooleanField(default=False) # a superuser

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name',]

    def get_full_name(self):
        return self.first_name, self.last_name

    def get_short_name(self):
        return self.first_name

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        return self.staff

    @property
    def is_admin(self):
        "Is the user a admin member?"
        return self.admin

    objects = UserManager()
