import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    class Role(models.TextChoices):
        RECRUITER = "RECRUITER", "Recruiter"
        CANDIDATE = "CANDIDATE", "Candidate"

    pkid = models.BigAutoField(primary_key=True, editable=False)
    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    
    email = models.EmailField(_("email address"), unique=True)
    
    role = models.CharField(
        max_length=50, 
        choices=Role.choices, 
        default=Role.CANDIDATE
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def __str__(self):
        return self.email