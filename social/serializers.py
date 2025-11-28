from django.db.models import Count
from social.models import Profile, Follow, Hashtag, Post, Comment, Like
from rest_framework import serializers


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ["id",
                  "first_name",
                  "last_name",
                  "bio",
                  "country_of_residence",
                  "picture"
                  ]


class ProfileListSerializer(ProfileSerializer):
    class Meta:
        model = Profile
        fields = ["first_name",
                  "last_name",
                  "bio",
                  "country_of_residence",
                  "picture"
                  ]


class ProfileImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ("id", "picture")


class PostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ("id", "picture")


class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = ["id", "followee"]


class HashtagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hashtag
        fields = ["id", "title"]


class PostSerializer(serializers.ModelSerializer):
    hashtags = serializers.PrimaryKeyRelatedField(
        queryset=Hashtag.objects.all(),
        many=True
    )

    class Meta:
        model = Post
        fields = ["id",
                  "text",
                  "created_at",
                  "scheduled_publish",
                  "hashtags"
                  ]


class PostListSerializer(PostSerializer):
    hashtags = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='title'
    )
    likes_count = serializers.IntegerField(read_only=True)
    comments_count = serializers.IntegerField(read_only=True)
    author_full_name = serializers.CharField(
        source="author.profile.full_name",
        read_only=True
    )

    class Meta:
        model = Post
        fields = ["id",
                  "author_full_name",
                  "text",
                  "created_at",
                  "edited",
                  "picture",
                  "hashtags",
                  "likes_count",
                  "comments_count"
                  ]


class CommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = ["id", "post", "created_at", "text"]


class CommentListSerializer(CommentSerializer):
    author_full_name = serializers.CharField(
        source="author.profile.full_name",
        read_only=True
    )

    class Meta:
        model = Comment
        fields = ["id", "author_full_name", "post", "created_at", "text"]


class PostDetailSerializer(PostSerializer):
    hashtags = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='title'
    )
    author_full_name = serializers.CharField(
        source="author.profile.full_name",
        read_only=True
    )
    likes_count = serializers.IntegerField(read_only=True)
    comments = CommentListSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = ["id",
                  "author_full_name",
                  "created_at",
                  "text",
                  "edited",
                  "picture",
                  "hashtags",
                  "likes_count",
                  "comments"
                  ]


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ["id", "post"]


class ProfileDetailSerializer(ProfileSerializer):
    posts = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ["first_name",
                  "last_name",
                  "bio",
                  "country_of_residence",
                  "picture",
                  "posts"
                  ]

    def get_posts(self, obj):
        qs = obj.author.posts.annotate(
            likes_count=Count("likes", distinct=True),
            comments_count=Count("comments", distinct=True)
        )
        return PostListSerializer(qs, many=True).data
