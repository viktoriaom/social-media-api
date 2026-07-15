from django.contrib import admin

from social.models import (
    Profile,
    Post,
    Follow,
    Like,
    Hashtag,
    Comment
)

admin.site.register(Profile)
admin.site.register(Post)
admin.site.register(Follow)
admin.site.register(Like)
admin.site.register(Hashtag)
admin.site.register(Comment)
