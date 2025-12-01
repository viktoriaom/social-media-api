from io import BytesIO
from PIL.Image import Image
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from social.models import Profile
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.core.cache import cache
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from social.serializers import (
    ProfileListSerializer,
    ProfileDetailSerializer,
    ProfileImageSerializer,
    ProfileSerializer
)
from social.tests.helpers import create_test_profile, create_and_login_user
from social.views import ProfileViewSet


PAGE_SIZE = settings.base.REST_FRAMEWORK.get("PAGE_SIZE", 10)
PROFILE_URL = reverse("social:profiles-list")


def detail_url(profile_id):
    return reverse("social:profile-detail", kwargs={"pk": profile_id})


class ModelsTests(TestCase):

    def test_profile_str_and_full_name(self):
        profile = create_test_profile()
        self.assertEqual(str(profile), profile.first_name + " " + profile.last_name)
        self.assertEqual(profile.full_name,
                         profile.first_name + " " + profile.last_name)


class GetTokensTests(TestCase):
    def setUp(self):
        cache.clear()
        self.client = APIClient()

    def test_tokens(self):
        get_user_model().objects.create_user(
            email="test@example.com", password="testpass123"
        )
        response = self.client.post(
            "/api/user/token/",
            {"email": "test@example.com", "password": "testpass123"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

        refresh_token = response.data["refresh"]

        refresh_res = self.client.post(
            "/api/user/token/refresh/", {"refresh": refresh_token}
        )

        self.assertEqual(refresh_res.status_code, 200)
        self.assertIn("access", refresh_res.data)

    def test_list_profiles_missing_token(self):
        self.client.credentials()  # Remove token
        res = self.client.get(PROFILE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_profiles_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION="Bearer invalidtoken123")
        res = self.client.get(PROFILE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class UnauthenticatedProfileViewSetTests(TestCase):
    def setUp(self):
        cache.clear()
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(PROFILE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedProfileViewSetTests(TestCase):
    def setUp(self):
        cache.clear()
        self.user, self.client = create_and_login_user()

    def test_list_profiles(self):
        for _ in range(5):
            create_test_profile()
        res = self.client.get(PROFILE_URL)
        profiles = Profile.objects.all()
        serializer = ProfileListSerializer(profiles, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_paginated_list_plays(self):
        profiles_count = PAGE_SIZE + (PAGE_SIZE // 2)
        for _ in range(profiles_count):
            create_test_profile()
        res = self.client.get(PROFILE_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("results", res.data)
        self.assertIn("count", res.data)
        self.assertIn("next", res.data)
        self.assertIn("previous", res.data)
        self.assertEqual(len(res.data["results"]), PAGE_SIZE)
        self.assertEqual(res.data["count"], profiles_count)
        self.assertIsNotNone(res.data["next"])
        self.assertIsNone(res.data["previous"])
        res_page_2 = self.client.get(
            PROFILE_URL, {"limit": PAGE_SIZE, "offset": PAGE_SIZE}
        )
        self.assertEqual(res_page_2.status_code, status.HTTP_200_OK)
        self.assertEqual(
            len(res_page_2.data["results"]),
            profiles_count - PAGE_SIZE
        )
        self.assertIsNone(res_page_2.data["next"])
        self.assertIsNotNone(res_page_2.data["previous"])

    def test_filter_by_first_name_profile(self):
        profile_one = create_test_profile(first_name="Andy")
        profile_two = create_test_profile(first_name="Xenia")

        res = self.client.get(PROFILE_URL, {"first_name": f"{profile_one.first_name}"})
        serializer_one = ProfileListSerializer(profile_one)
        serializer_two = ProfileListSerializer(profile_two)

        self.assertIn(serializer_one.data, res.data["results"])
        self.assertNotIn(serializer_two.data, res.data["results"])

        res = self.client.get(PROFILE_URL, {"title": "mo"})
        self.assertIn(serializer_one.data, res.data["results"])
        self.assertNotIn(serializer_two.data, res.data["results"])

    def test_filter_by_last_name_profile(self):
        profile_one = create_test_profile(last_name="Mcferrin")
        profile_two = create_test_profile(last_name="Swift")

        res = self.client.get(PROFILE_URL, {"last_name": f"{profile_one.last_name}"})
        serializer_one = ProfileListSerializer(profile_one)
        serializer_two = ProfileListSerializer(profile_two)

        self.assertIn(serializer_one.data, res.data["results"])
        self.assertNotIn(serializer_two.data, res.data["results"])

        res = self.client.get(PROFILE_URL, {"title": "mo"})
        self.assertIn(serializer_one.data, res.data["results"])
        self.assertNotIn(serializer_two.data, res.data["results"])

    def test_filter_by_country_of_residence_plays(self):
        profile_one = create_test_profile(country_of_residence="Ukraine")
        profile_two = create_test_profile(country_of_residence="Portugal")

        res = self.client.get(PROFILE_URL, {"country_of_residence": f"{profile_one.country_of_residence}"})
        serializer_one = ProfileListSerializer(profile_one)
        serializer_two = ProfileListSerializer(profile_two)

        self.assertIn(serializer_one.data, res.data["results"])
        self.assertNotIn(serializer_two.data, res.data["results"])

        res = self.client.get(PROFILE_URL, {"title": "mo"})
        self.assertIn(serializer_one.data, res.data["results"])
        self.assertNotIn(serializer_two.data, res.data["results"])

    def test_detail_profile(self):
        profile = create_test_profile()
        res = self.client.get(detail_url(profile.id))
        serializer = ProfileDetailSerializer(profile)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_profile(self):
        payload = {
            "first_name": "Xenia",
            "last_name": "Swift",
            "bio": "Test bio",
            "country_of_residence": "Test country"
        }
        res = self.client.post(PROFILE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        profile = Profile.objects.get(author=self.user)
        self.assertEqual(profile.first_name, payload["first_name"])
        self.assertEqual(profile.last_name, payload["last_name"])
        self.assertEqual(profile.bio, payload["bio"])
        self.assertEqual(profile.country_of_residence, payload["country_of_residence"])


    def test_put_profile(self):
        profile = create_test_profile(author=self.user)
        payload = {
            "first_name": "New First Name",
            "last_name": "New Last Name",
            "bio": "New Bio",
            "country_of_residence": "New Country"
        }
        profile_to_put_url = detail_url(profile.id)
        res = self.client.put(profile_to_put_url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        profile.refresh_from_db()
        self.assertEqual(payload["first_name"], profile.first_name)
        self.assertEqual(payload["last_name"], profile.last_name)

        self.assertEqual(res.data["first_name"], payload["first_name"])
        self.assertEqual(res.data["last_name"], payload["last_name"])
        self.assertEqual(res.data["bio"], payload["bio"])
        self.assertEqual(res.data["country_of_residence"], payload["country_of_residence"])

    def test_patch_play_admin(self):
        profile = create_test_profile(author=self.user)
        payload = {
            "country_of_residence": "New Country",
        }
        profile_to_patch_url = detail_url(profile.id)
        res = self.client.patch(profile_to_patch_url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        profile.refresh_from_db()
        self.assertEqual(res.data["country_of_residence"], payload["country_of_residence"])

    def test_delete_play_admin(self):
        profile = create_test_profile(author=self.user)
        serializer = ProfileListSerializer(profile)
        res = self.client.get(PROFILE_URL)
        self.assertIn(serializer.data, res.data["results"])
        profile_to_delete_url = detail_url(profile.id)
        res = self.client.delete(profile_to_delete_url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_add_image_to_profile(self):
        profile = create_test_profile(author=self.user)
        url = reverse("social:profiles-upload-image", kwargs={"pk": profile.id})
        image_io = BytesIO()
        image = Image.new("RGB", (100, 100), color="red")
        image.save(image_io, format="JPEG")
        image_io.seek(0)
        uploaded_image = SimpleUploadedFile(
            name="test.jpg", content=image_io.read(), content_type="image/jpeg"
        )

        res = self.client.post(
            url,
            {"image": uploaded_image},
            format="multipart"
        )
        profile.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("image", res.data)
        self.assertTrue(profile.image.name.endswith(".jpg"))


class ProfileViewSetSerializerClassTest(TestCase):
    def setUp(self):
        self.viewset = ProfileViewSet()

    def test_list_action_uses_list_serializer(self):
        self.viewset.action = "list"
        serializer_class = self.viewset.get_serializer_class()
        self.assertEqual(serializer_class, ProfileListSerializer)

    def test_retrieve_action_uses_detail_serializer(self):
        self.viewset.action = "retrieve"
        serializer_class = self.viewset.get_serializer_class()
        self.assertEqual(serializer_class, ProfileDetailSerializer)

    def test_upload_image_action_uses_image_serializer(self):
        self.viewset.action = "upload_image"
        serializer_class = self.viewset.get_serializer_class()
        self.assertEqual(serializer_class, ProfileImageSerializer)

    def test_default_action_uses_base_serializer(self):
        self.viewset.action = "create"
        serializer_class = self.viewset.get_serializer_class()
        self.assertEqual(serializer_class, ProfileSerializer)
