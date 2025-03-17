from django.contrib import admin
from .models import Team, JoinRequest, SupervisorRequest


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('id', 'thesis_topic', 'owner', 'supervisor', 'status')
    search_fields = ('thesis_topic__title', 'owner__email', 'supervisor__user__email')
    list_filter = ('status',)

@admin.register(JoinRequest)
class JoinRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'team', 'status', 'created_at')
    list_filter = ('status', 'team')
    search_fields = ('student__user__email', 'team__thesis_topic__title')
    ordering = ('-created_at',)

@admin.register(SupervisorRequest)
class SupervisorRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'team', 'supervisor', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('team__thesis_topic__title', 'supervisor__user__email')
    autocomplete_fields = ('team', 'supervisor')
    ordering = ('-created_at',)