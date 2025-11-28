from django.db.models import Count
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from social.models import Profile, Comment, Follow, Hashtag, Post, Like
from social.serializers import (
    ProfileSerializer,
    CommentSerializer,
    FollowSerializer,
    HashtagSerializer,
    PostSerializer,
    LikeSerializer,
    ProfileDetailSerializer,
    ProfileListSerializer,
    PostListSerializer,
    PostDetailSerializer,
    CommentListSerializer,
    ProfileImageSerializer,
    PostImageSerializer
)


class ProfileViewSet(viewsets.ModelViewSet):

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return ProfileListSerializer
        elif self.action == 'retrieve':
            return ProfileDetailSerializer
        elif self.action == "upload_image":
            return ProfileImageSerializer
        return ProfileSerializer

    def get_queryset(self):
        queryset = Profile.objects.all()

        first_name = self.request.query_params.get("first_name")
        last_name = self.request.query_params.get("last_name")
        country_of_residence = self.request.query_params.get(
            "country_of_residence"
        )

        if first_name:
            queryset = queryset.filter(first_name__icontains=first_name)
        if last_name:
            queryset = queryset.filter(last_name__icontains=last_name)
        if country_of_residence:
            queryset = queryset.filter(
                country_of_residence__icontains=country_of_residence
            )

        # list of users authenticated user is following
        if self.request.query_params.get("following") == "true":
            following_ids = self.request.user.following.values_list(
                "followee_id",
                flat=True
            )
            queryset = queryset.filter(author__id__in=following_ids)

        # list of users authenticated user is followed by
        if self.request.query_params.get("follower") == "true":
            follower_ids = self.request.user.follower.values_list(
                "author_id",
                flat=True
            )
            queryset = queryset.filter(author__id__in=follower_ids)

        return queryset.distinct()

    @action(
        methods=["POST"],
        detail=True,
        url_path="upload-image"
    )
    def upload_image(self, request, pk=None):
        """Endpoint for uploading image to profile"""
        profile = self.get_object()
        serializer = self.get_serializer(profile, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="first_name",
                type={"type": "str"},
                description="Filter by first_name (ex. ?first_name=Andy)",
            ),
            OpenApiParameter(
                name="last_name",
                type={"type": "str"},
                description="Filter by last_name (ex. ?last_name=McFerrin)",
            ),
            OpenApiParameter(
                name="country_of_residence",
                type={"type": "str"},
                description="Filter by country_of_residence (ex. ?country_of_residence=Ukraine)",
            ),
            OpenApiParameter(
                name="following",
                type={"type": "str"},
                description="Filter profiles of users that the authenticated user is following (ex. ?following=true)",
            ),
            OpenApiParameter(
                name="follower",
                type={"type": "str"},
                description="Filter profiles of users the authenticated user is followed by (ex. ?follower=true)",
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        """Get list of performances."""
        return super().list(request, *args, **kwargs)


class FollowViewSet(viewsets.ModelViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class HashtagViewSet(viewsets.ModelViewSet):
    queryset = Hashtag.objects.all()
    serializer_class = HashtagSerializer

    def perform_create(self, serializer):
        serializer.save(title="#" + serializer.validated_data["title"])


class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return PostListSerializer
        if self.action == "retrieve":
            return PostDetailSerializer
        elif self.action == "upload_image":
            return PostImageSerializer
        return PostSerializer

    def get_queryset(self):
        queryset = (Post.objects.all().filter(published=True).annotate(
            likes_count=Count('likes', distinct=True),
            comments_count=Count('comments', distinct=True)))

        # filter posts where authenticated user is the author
        if self.request.query_params.get("mine") == "true":
            queryset = queryset.filter(author=self.request.user)

        # filter posts of users that authenticated user is following
        if self.request.query_params.get("following") == "true":
            following_ids = self.request.user.following.values_list(
                "followee_id",
                flat=True
            )
            queryset = queryset.filter(author__id__in=following_ids)

        # filter posts of users that authenticated user has liked
        if self.request.query_params.get("liked") == "true":
            liked_ids = Like.objects.filter(
                author=self.request.user).values_list(
                "post_id", flat=True)
            queryset = queryset.filter(id__in=liked_ids)

        # filter posts by hashtags text
        hashtag_str = self.request.query_params.get("hashtags")
        if hashtag_str:
            queryset = queryset.filter(hashtags__title__icontains=hashtag_str)

        return queryset

    @action(
        methods=["POST"],
        detail=True,
        url_path="upload-image"
    )
    def upload_image(self, request, pk=None):
        """Endpoint for uploading image to post"""
        post = self.get_object()
        serializer = self.get_serializer(post, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="mine",
                type={"type": "str"},
                description="Filter posts where authenticated user is the author (ex. ?mine=true)",
            ),
            OpenApiParameter(
                name="following",
                type={"type": "str"},
                description="Filter posts of users that authenticated user is following (ex. ?following=true)",
            ),
            OpenApiParameter(
                name="liked",
                type={"type": "str"},
                description="Filter posts of users that authenticated user has liked (ex. ?liked=true)",
            ),
            OpenApiParameter(
                name="hashtags",
                type={"type": "str"},
                description="Filter posts by hashtags text (ex. ?hashtags=love)",
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        """Get list of performances."""
        return super().list(request, *args, **kwargs)


class LikeViewSet(viewsets.ModelViewSet):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_queryset(self):
        queryset = Comment.objects.all()
        post_id = self.request.query_params.get("post_id")
        return queryset.filter(pk=post_id)

    def get_serializer_class(self):
        if self.action == "list":
            return CommentListSerializer
        return CommentSerializer
