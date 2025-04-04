from django.urls import path
from .views import (
    NotificationListView,
    NotificationUnreadCountView,
    DeleteNotification, MarkAllAsRead,
)

urlpatterns = [
    path('', NotificationListView.as_view(), name='notification-list'),
    path('unread/', NotificationUnreadCountView.as_view(), name='unread'),
    path('mark-all-as-read/', MarkAllAsRead.as_view(), name='mark-all-as-read'),
    path('<int:pk>/', DeleteNotification.as_view(), name='delete-notification'),
]
