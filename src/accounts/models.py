from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.utils import timezone
from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
import pytz
import random
import string


class UserManager(BaseUserManager):
    """
    Creates and saves a User with the given email, phone, password and optional extra info.
    """
    def _create_user(self, email,
                     name,
                     password,
                     is_staff, is_superuser, **extra_fields):
        """
        Creates and saves a User with the given username, email and password.
        """
        now = timezone.now()

        if not email:
            raise ValueError('The given email must be set')

        email = self.normalize_email(email)
        user = self.model(
            email=email,
            name=name or '',
            is_staff=is_staff, is_active=True,
            is_superuser=is_superuser,
            date_joined=now,
            last_login=now,
            **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, name, password=None, **extra_fields):
        return self._create_user(email, name, password, False, False, **extra_fields)

    def create_superuser(
            self, email, name, password=None, **extra_fields):
        """
        Creates and saves a superuser with the given email,
        phone and password.
        """
        return self._create_user(email, name, password, True, True, **extra_fields)

    def get_by_natural_key(self, email):
        return self.get(email__iexact=email)


class User(AbstractBaseUser, PermissionsMixin):
    """
    A model which implements the authentication model.

    Email and password are required. Other fields are optional.

    Email field are used for logging in.
    """
    email = models.EmailField(_('Email'), max_length=255, unique=True)
    name = models.CharField(_('Full name'), max_length=255)

    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )

    date_joined = models.DateTimeField(_('Date joined'), default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        ordering = ['name', '-date_joined']

    def get_first_name(self):
        chunks = self.name.split()
        if len(chunks) >= 1:
            return chunks[0]
        else:
            return ''

    @property
    def first_name(self):
        return self.get_first_name()

    def get_last_name(self):
        chunks = self.name.split()
        if len(chunks) >= 2:
            return chunks[1]
        else:
            return ''

    @property
    def last_name(self):
        return self.get_last_name()

    def __str__(self):
        return self.name

    def get_email_md5_hash(self):
        import hashlib
        m = hashlib.md5(self.email.lower().encode('utf-8')).hexdigest()
        return m

    def has_usable_password(self) -> bool:
        return super().has_usable_password()
    has_usable_password.boolean = True

    @property
    def days_on_site(self):
        from django.utils.timezone import now
        delta = now() - self.date_joined
        return delta.days
