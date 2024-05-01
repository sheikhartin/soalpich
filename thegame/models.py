import uuid

from django.db import models
from django.contrib.auth.models import AbstractUser


def _upload_to(_: "CustomUser", filename: str) -> str:
    """Creates a path with a unique ID for the image."""
    return f'profile_pics/{uuid.uuid4()}.{filename.split(".")[-1]}'


def _generate_unique_slug() -> int:
    """Produces a unique slug."""
    return uuid.uuid4().int % 100_000_000


class CustomUser(AbstractUser):
    username = models.CharField(max_length=150, unique=True)
    profile_picture = models.ImageField(
        upload_to=_upload_to, blank=True, null=True, default="images/logo.png"
    )
    scores = models.IntegerField(default=0)
    is_email_public = models.BooleanField(default=False)
    instagram_username = models.CharField(max_length=30, blank=True, null=True)
    facebook_username = models.CharField(max_length=50, blank=True, null=True)
    twitter_username = models.CharField(max_length=50, blank=True, null=True)
    telegram_username = models.CharField(max_length=32, blank=True, null=True)


class Question(models.Model):
    text = models.CharField(max_length=512)
    options = models.JSONField()


class QuizRoom(models.Model):
    creator = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="created_rooms"
    )
    slug = models.SlugField(default=_generate_unique_slug, unique=True)
    questions = models.ManyToManyField(Question)  # Fixed questions for the room
    created_at = models.DateTimeField(auto_now_add=True)
    players = models.ManyToManyField(
        CustomUser, related_name="joined_rooms", blank=True
    )


class UserAnswer(models.Model):
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="answers"
    )
    room = models.ForeignKey(QuizRoom, on_delete=models.CASCADE, related_name="answers")
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    is_correct = models.BooleanField()
