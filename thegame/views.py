from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.views.generic import TemplateView, View
from django.http import HttpRequest, HttpResponse
from django.contrib.auth import get_user_model, login, logout, authenticate
from django.contrib.auth.hashers import make_password
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q

from thegame import models

User = get_user_model()


class IndexView(TemplateView):
    template_name = "index.html"


class ProfileView(LoginRequiredMixin, View):
    login_url = "/register/"

    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, "profile.html", {"user": request.user})

    def post(self, request: HttpRequest) -> HttpResponse:
        if (user := request.user) and User.objects.filter(
            Q(username=(username := request.POST.get("username")))
            | Q(email=(email := request.POST.get("email"))),
            ~Q(id=user.id),
        ).exists():
            return render(
                request,
                "profile.html",
                {
                    "user": request.user,
                    "error": "Username and/or e-mail already taken.",
                },
            )

        user.username = username if username is not None else user.username
        user.email = email if email is not None else user.email
        user.is_email_public = "is_email_public" in request.POST
        user.instagram_username = request.POST.get(
            "instagram_username", user.instagram_username
        )
        user.facebook_username = request.POST.get(
            "facebook_username", user.facebook_username
        )
        user.twitter_username = request.POST.get(
            "twitter_username", user.twitter_username
        )
        user.telegram_username = request.POST.get(
            "telegram_username", user.telegram_username
        )
        if new_password := request.POST.get("new_password"):
            user.password = make_password(new_password)
        if profile_picture := request.FILES.get("profile_picture"):
            user.profile_picture.save(profile_picture.name, profile_picture)
        user.save()
        return redirect("profile")


class PublicProfileView(View):
    def get(self, request: HttpRequest, **kwargs: str) -> HttpResponse:
        return render(
            request,
            "public_profile.html",
            {
                "profile_user": get_object_or_404(
                    User, username=kwargs.get("username"), is_active=True
                )
            },
        )


class LoggedOutOnlyMixin(UserPassesTestMixin):
    def test_func(self) -> bool:
        return not self.request.user.is_authenticated

    def handle_no_permission(self) -> HttpResponse:
        return redirect("profile")


class LoginView(LoggedOutOnlyMixin, View):
    def post(self, request: HttpRequest) -> HttpResponse:
        if (
            user := authenticate(
                request,
                username=request.POST.get("username"),
                password=request.POST.get("password"),
            )
        ) is not None:
            login(request, user)
            return redirect("profile")
        return render(request, "register.html", {"error": "Invalid credentials!"})


class RegisterView(LoggedOutOnlyMixin, View):
    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, "register.html")

    def post(self, request: HttpRequest) -> HttpResponse:
        if User.objects.filter(
            Q(username=(username := request.POST.get("username")))
            | Q(email=(email := request.POST.get("email")))
        ).exists():
            return render(
                request,
                "register.html",
                {
                    "error": "The username and/or e-mail you entered has been used by another account!"
                },
            )
        user = User.objects.create(
            username=username,
            email=email,
            password=make_password(request.POST.get("password")),
        )
        user.full_clean()
        user.save()
        login(request, user)
        return redirect("profile")


class LogoutView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        logout(request)
        return redirect("index")


class NotFoundErrorView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, "404.html", status=404)


class GamesRoomView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        return render(
            request,
            "games_room.html",
            {
                "games": Paginator(
                    models.QuizRoom.objects.all().order_by("-created_at"), 15
                ).get_page(request.GET.get("page"))
            },
        )

    def post(self, request: HttpRequest) -> HttpResponse:
        if not request.user.is_authenticated:
            return redirect("register")
        new_room = models.QuizRoom.objects.create(creator=request.user)
        new_room.questions.set(
            models.Question.objects.order_by("?")[
                : int(request.POST.get("num_questions", 6))
            ]
        )
        new_room.save()
        return redirect("play", slug=new_room.slug)


class PlayView(LoginRequiredMixin, View):
    login_url = "/register/"

    def get(self, request: HttpRequest, **kwargs: str) -> HttpResponse:
        if (
            (room := get_object_or_404(models.QuizRoom, slug=kwargs.get("slug")))
            .players.filter(id=request.user.id)
            .exists()
        ):
            return render(
                request,
                "play.html",
                {
                    "room": room,
                    "user_answers": models.UserAnswer.objects.filter(
                        user=request.user, room=room
                    ),
                    "played": True,
                },
            )
        return render(
            request,
            "play.html",
            {"room": room, "questions": room.questions.all(), "played": False},
        )

    def post(self, request: HttpRequest, **kwargs: str) -> HttpResponse:
        if (
            (
                room := get_object_or_404(
                    models.QuizRoom, slug=(slug := kwargs.get("slug"))
                )
            )
            .players.filter(id=request.user.id)
            .exists()
        ):
            return redirect("play", slug=slug)

        scores = 0
        for question in room.questions.all():
            scores += (
                1
                if (
                    is_correct := question.options[request.POST.get(str(question.id))]
                    == True
                )
                else -1
            )
            models.UserAnswer.objects.create(
                user=request.user, room=room, question=question, is_correct=is_correct
            )
        request.user.scores += scores
        request.user.save()
        room.players.add(request.user)
        room.save()
        return redirect("play", slug=slug)
