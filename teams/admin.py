from django.contrib import admin
from .models import Team

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('id', 'thesis_topic', 'owner', 'supervisor', 'status')
    search_fields = ('thesis_topic__title', 'owner__email', 'supervisor__user__email')
    list_filter = ('status',)