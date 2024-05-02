from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from thegame import models

User = get_user_model()


class IndexViewTest(TestCase):
    def test_index_view(self) -> None:
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "index.html")


class ProfileViewTest(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="testpass")

    def test_profile_view_get(self) -> None:
        self.client.force_login(self.user)
        response = self.client.get(reverse("profile"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "profile.html")

    def test_profile_view_post(self) -> None:
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("profile"),
            {"username": "newusername", "email": "newemail@example.com"},
        )
        self.assertRedirects(response, reverse("profile"))


class PublicProfileViewTest(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.user = User.objects.create_user(
            username="publicuser", password="testpass", is_active=True
        )

    def test_public_profile_view(self) -> None:
        response = self.client.get(
            reverse("public_profile", kwargs={"username": "publicuser"})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "public_profile.html")


class RegisterViewTest(TestCase):
    def test_register_view_get(self) -> None:
        response = self.client.get(reverse("register"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "register.html")

    def test_register_view_post(self) -> None:
        response = self.client.post(
            reverse("register"),
            {
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "newpass",
            },
        )
        self.assertRedirects(response, reverse("profile"))


class NotFoundErrorViewTest(TestCase):
    def test_not_found_error_view(self) -> None:
        response = self.client.get("/nonexistentpage/")
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, "404.html")


class GamesRoomViewTest(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.user = User.objects.create_user(
            username="testgamesroom", password="testpass"
        )

    def test_games_room_view_get(self) -> None:
        response = self.client.get(reverse("games_room"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "games_room.html")

    def test_games_room_view_post(self) -> None:
        self.client.force_login(self.user)
        response = self.client.post(reverse("games_room"), {"num_questions": 5})
        self.assertEqual(response.status_code, 302)  # Redirect to play view


class PlayViewTest(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.user = User.objects.create_user(username="testplay", password="testpass")
        self.room = models.QuizRoom.objects.create(creator=self.user)
        self.question = models.Question.objects.create(
            text="A silly question?!",
            options={"A": False, "B": False, "C": True, "D": False},
        )
        self.room.questions.add(self.question)

    def test_play_view_get(self) -> None:
        self.client.force_login(self.user)
        response = self.client.get(reverse("play", kwargs={"slug": self.room.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "play.html")

    def test_play_view_post(self) -> None:
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("play", kwargs={"slug": self.room.slug}), {self.question.id: "B"}
        )
        self.assertRedirects(response, reverse("play", kwargs={"slug": self.room.slug}))
