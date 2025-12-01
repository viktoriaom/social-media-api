from uuid import uuid4
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from social.models import Profile


def create_and_login_user(**params):
    defaults = {
        "email": f"user_{uuid4().hex[:8]}@example.com",
        "password": "testpass123",
        "is_staff": False,
    }
    defaults.update(params)
    client = APIClient()
    user = get_user_model().objects.create_user(**defaults)
    response = client.post(
        "/api/user/token/",
        {"email": defaults["email"], "password": defaults["password"]},
    )
    token = response.data["access"]
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return user, client


def create_test_profile(**params) -> Profile:
    if "author" not in params:
        user, client = create_and_login_user(**params)
        params["author"] = user

    defaults = {"first_name": f"First {uuid4().hex[:6]}",
                "last_name": f"Last {uuid4().hex[:6]}",
                "bio": "Test bio",
                "country_of_residence": f"Country {uuid4().hex[:6]}"
                }
    defaults.update(params)
    return Profile.objects.create(**defaults)
