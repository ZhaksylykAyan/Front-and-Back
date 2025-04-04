from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, AccessLog


@admin.register(CustomUser)
class UserAdmin(UserAdmin):
    model = CustomUser
    list_display = (
        'id','email', 'role', 'is_profile_completed', 'is_staff',
        'failed_login_attempts', 'is_blocked', 'last_login_ip'
    )
    list_filter = ('role', 'is_staff', 'is_blocked')
    search_fields = ('email',)
    ordering = ('email',)
    readonly_fields = ('last_login_ip',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_superuser', 'is_active')}),
        ('Role/Profile', {'fields': ('role', 'is_profile_completed')}),
        ('Security', {'fields': ('failed_login_attempts', 'is_blocked', 'last_login_ip')}),
        ('Groups', {'fields': ('groups', 'user_permissions')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'role', 'is_staff', 'is_superuser', 'is_active')}
        ),
    )
@admin.register(AccessLog)
class AccessLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'timestamp', 'ip_address')
    list_filter = ('action', 'timestamp')
    search_fields = ('user__email', 'ip_address', 'user_agent')
    ordering = ('-timestamp',)
