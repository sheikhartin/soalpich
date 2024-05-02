import json

from django.contrib.auth import get_user_model
from django.utils import timezone
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

from letstalk import models

User = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self) -> None:
        if not self.scope["user"].is_authenticated:
            await self.close()
            return None
        self.room_group_name = "chat_room"
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code: int) -> None:
        if self.scope["user"].is_anonymous:
            return None
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data: str) -> None:
        if (
            command := (text_data_json := json.loads(text_data)).get("command")
        ) == "send":
            if message_text := text_data_json.get("message", "").strip():
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type": "new_chat_message",
                        "message_id": (
                            message := await self.save_message_to_db(
                                self.scope["user"], message_text
                            )
                        ).id,
                        "author": message.user.username,
                        "message": message.text,
                        "timestamp": (
                            timezone.localtime(message.timestamp).strftime(
                                "%b %d %H:%M"
                            )
                        ),
                        "profile_picture_url": message.user.profile_picture.url,
                        "can_delete": (
                            self.scope["user"] == message.user
                            or self.scope["user"].is_superuser
                        ),
                    },
                )
        elif command == "delete":
            if await self.delete_message_from_db(
                self.scope["user"], (message_id := text_data_json.get("message_id"))
            ):
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {"type": "chat_message_delete", "message_id": message_id},
                )
        return None

    @database_sync_to_async
    def save_message_to_db(self, user: User, message_text: str) -> models.Message:
        return models.Message.objects.create(user=user, text=message_text)

    async def new_chat_message(self, event: dict) -> None:
        await self.send(
            text_data=json.dumps(
                {
                    "command": "new_message",
                    "message": {
                        "id": event["message_id"],
                        "author": event["author"],
                        "text": event["message"],
                        "timestamp": event["timestamp"],
                        "profile_picture_url": event["profile_picture_url"],
                        "can_delete": event["can_delete"],
                    },
                }
            )
        )

    @database_sync_to_async
    def delete_message_from_db(
        self,
        user: User,
        message_id: int,
    ) -> bool:
        try:
            if (
                user != (message := models.Message.objects.get(id=message_id)).user
                and not user.is_superuser
            ):
                return False
            message.delete()
            return True
        except models.Message.DoesNotExist:
            return False

    async def chat_message_delete(self, event: dict) -> None:
        await self.send(
            text_data=json.dumps(
                {
                    "command": "delete_message",
                    "message_id": event["message_id"],
                }
            )
        )
