from django.urls import path

from letstalk import views

urlpatterns = [
    path("chat/", views.ChatRoomView.as_view(), name="chat_room"),
]
