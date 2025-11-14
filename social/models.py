from django.db import models

from social_media_api import settings


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
        null=True, blank=True
    )  # TODO upload to part > upload_to="images/"

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
    picture = models.ImageField(
        upload_to="images/", null=True, blank=True
    )  # TODO upload to part
    scheduled_publish = models.DateTimeField(null=True, blank=True)
    hashtags = models.ManyToManyField(
        Hashtag,
        blank=True,
        related_name="posts"
    )

    class Meta:
        ordering = ["-created_at"]


class Like(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    post = models.ForeignKey(Post, on_delete=models.CASCADE)


class Comment(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
