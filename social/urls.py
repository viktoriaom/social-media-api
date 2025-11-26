from django.urls import path, include
from rest_framework import routers

from social.views import (
    ProfileViewSet,
    CommentViewSet,
    LikeViewSet,
    FollowViewSet,
    HashtagViewSet,
    PostViewSet
)

router = routers.DefaultRouter()
router.register("profiles", ProfileViewSet, basename="profiles")
router.register("likes", LikeViewSet, basename="likes")
router.register("follows", FollowViewSet, basename="follows")
router.register("hashtags", HashtagViewSet, basename="hashtags")
router.register("posts", PostViewSet, basename="posts")
router.register("comments", CommentViewSet, basename="comments")


urlpatterns = [path("", include(router.urls))]

app_name = "social"
