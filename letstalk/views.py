from django.shortcuts import render, get_object_or_404
from django.views.generic import View
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

from letstalk import models


class ChatRoomView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        return render(
            request,
            "chat_room.html",
            {"messages": models.Message.objects.order_by("timestamp")},
        )

    def post(self, request: HttpRequest) -> JsonResponse:
        if not request.user.is_authenticated:
            return JsonResponse(
                {"status": "error", "message": "You must be logged in to do this."},
                status=401,
            )
        elif "delete_message_id" in request.POST:
            if (
                request.user
                != (
                    message := get_object_or_404(
                        models.Message, id=request.POST.get("delete_message_id")
                    )
                ).user
                and not request.user.is_superuser
            ):
                return JsonResponse(
                    {
                        "status": "error",
                        "message": "You do not have permission to delete this message!",
                    },
                    status=403,
                )
            message.delete()
            return JsonResponse({"status": "success"})
        elif not (message_text := request.POST.get("message", "").strip()):
            return JsonResponse(
                {
                    "status": "error",
                    "message": "No message provided!",
                },
                status=400,
            )
        models.Message.objects.create(user=request.user, text=message_text)
        return JsonResponse({"status": "success", "message": message_text})
