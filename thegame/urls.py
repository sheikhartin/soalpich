from django.urls import path

from thegame import views

handler404 = views.NotFoundErrorView.as_view()

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path(
        "users/<str:username>/",
        views.PublicProfileView.as_view(),
        name="public_profile",
    ),
    path("login/", views.LoginView.as_view(), name="login"),
    path("register/", views.RegisterView.as_view(), name="register"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("games/", views.GamesRoomView.as_view(), name="games_room"),
    path("play/<slug:slug>/", views.PlayView.as_view(), name="play"),
]
