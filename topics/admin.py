from django.contrib import admin
from .models import ThesisTopic

@admin.register(ThesisTopic)
class ThesisTopicAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'created_by_student', 'created_by_supervisor')
    search_fields = ('title',)
    list_filter = ('created_by_student', 'created_by_supervisor')