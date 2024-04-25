from django.contrib import admin

from thegame.models import CustomUser, Question, QuizRoom, UserAnswer

admin.site.register(CustomUser)
admin.site.register(Question)
admin.site.register(QuizRoom)
admin.site.register(UserAnswer)
