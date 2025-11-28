from django.utils import timezone
from datetime import timedelta
from celery import shared_task
from social.models import Post


@shared_task
def publish_posts():

    now = timezone.now()

    start_of_hour = now.replace(minute=0, second=0, microsecond=0)
    end_of_hour = start_of_hour + timedelta(hours=1)

    posts_to_publish = Post.objects.filter(
        published=False,
        scheduled_publish__gte=start_of_hour,
        scheduled_publish__lt=end_of_hour
    )

    for post in posts_to_publish:
        post.published = True
        post.save()

    return posts_to_publish.count()
