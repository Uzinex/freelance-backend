from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from datetime import timedelta


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True, null=True, blank=True)
    phone = models.CharField(max_length=20, unique=True, null=True, blank=True)
    role = models.CharField(
        choices=[
            ("admin", "Admin"),
            ("customer", "Customer"),
            ("freelancer", "Freelancer"),
        ],
        default="freelancer",
        max_length=20,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username or self.email or self.phone or ''

    def average_rating(self):
        reviews = self.reviews_received.all()
        if not reviews:
            return None
        return sum(r.rating for r in reviews) / len(reviews)


class PasswordResetCode(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='reset_codes')
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def is_valid(self):
        return not self.is_used and timezone.now() - self.created_at < timedelta(minutes=10)

    def __str__(self):
        return f"{self.user} - {self.code}"
