from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Utilisateur, Quiz, Question, Tentative

# Register your models here.

admin.site.register(Utilisateur, UserAdmin)
admin.site.register(Quiz)
admin.site.register(Question)
admin.site.register(Tentative)
