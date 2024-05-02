from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

from letstalk import models

User = get_user_model()


class ChatRoomViewTest(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", password="testpass", is_active=True
        )
        self.superuser = User.objects.create_superuser(
            username="superuser", password="superpass", is_active=True
        )
        self.message_by_user = models.Message.objects.create(
            user=self.user, text="User Message"
        )
        self.message_by_superuser = models.Message.objects.create(
            user=self.superuser, text="Superuser Message"
        )

    def test_get_chat_room(self) -> None:
        response = self.client.get(reverse("chat_room"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.message_by_user.text)
        self.assertContains(response, self.message_by_superuser.text)

    def test_post_message_unauthenticated(self) -> None:
        response = self.client.post(reverse("chat_room"), {"message": "New Message"})
        self.assertEqual(response.status_code, 401)
        self.assertJSONEqual(
            response.content,
            {"status": "error", "message": "You must be logged in to do this."},
        )

    def test_post_message_no_message(self) -> None:
        self.client.force_login(self.user)
        response = self.client.post(reverse("chat_room"), {"message": ""})
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(
            response.content, {"status": "error", "message": "No message provided!"}
        )

    def test_post_message_success(self) -> None:
        self.client.force_login(self.user)
        response = self.client.post(reverse("chat_room"), {"message": "New Message"})
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content, {"status": "success", "message": "New Message"}
        )

    def test_delete_message_unauthenticated(self) -> None:
        response = self.client.post(
            reverse("chat_room"), {"delete_message_id": self.message_by_user.id}
        )
        self.assertEqual(response.status_code, 401)
        self.assertJSONEqual(
            response.content,
            {"status": "error", "message": "You must be logged in to do this."},
        )

    def test_delete_message_no_permission(self) -> None:
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("chat_room"), {"delete_message_id": self.message_by_superuser.id}
        )
        self.assertEqual(response.status_code, 403)
        self.assertJSONEqual(
            response.content,
            {
                "status": "error",
                "message": "You do not have permission to delete this message!",
            },
        )

    def test_delete_message_as_author(self) -> None:
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("chat_room"), {"delete_message_id": self.message_by_user.id}
        )
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"status": "success"})

    def test_delete_message_as_superuser(self) -> None:
        self.client.force_login(self.superuser)
        response = self.client.post(
            reverse("chat_room"), {"delete_message_id": self.message_by_user.id}
        )
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"status": "success"})
