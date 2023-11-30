from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Profile, Disciplina, Post, Comment, Reply, Arquivo

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'

class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline, )

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'tipo', 'biografia')
    list_filter = ('tipo',)
    search_fields = ['user__username', 'user__first_name', 'user__last_name']

admin.site.register(Profile, ProfileAdmin)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Disciplina)
admin.site.register(Reply)
admin.site.register(Arquivo)
