import os
import uuid
from django.utils import timezone

from django.db import models
from django.utils.text import slugify

from django.conf import settings


def profile_image_file_path(instance, filename):
    _, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.title)}-{uuid.uuid4()}{extension}"

    return os.path.join("uploads/profiles/", filename)


def post_image_file_path(instance, filename):
    _, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.title)}-{uuid.uuid4()}{extension}"

    return os.path.join("uploads/posts/", filename)


class Profile(models.Model):
    author = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    first_name = models.CharField(max_length=65)
    last_name = models.CharField(max_length=65)
    bio = models.TextField(max_length=300)
    country_of_residence = models.CharField(max_length=65)
    picture = models.ImageField(
        upload_to="profile_image_file_path", null=True, blank=True
    )

    def __str__(self):
        return self.first_name + " " + self.last_name

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Follow(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="following",
    )
    followee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="follower",
    )


class Hashtag(models.Model):
    title = models.CharField(max_length=65, unique=True)


class Post(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="posts",
    )
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(null=True, blank=True)
    picture = models.ImageField(
        upload_to="post_image_file_path", null=True, blank=True
    )
    scheduled_publish = models.DateTimeField(null=True, blank=True)
    published = models.BooleanField(default=False)
    hashtags = models.ManyToManyField(
        Hashtag,
        blank=True,
        related_name="posts"
    )

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        # if the object already exists (not a new post)
        if self.pk is not None:
            old = Post.objects.get(pk=self.pk)

            # Only update edited if content fields changed
            content_changed = (
                    old.text != self.text or
                    old.picture != self.picture or
                    old.hashtags.exists() != self.hashtags.exists()
            )

            if content_changed:
                self.edited = timezone.now()

        super().save(*args, **kwargs)


class Like(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")


class Comment(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
