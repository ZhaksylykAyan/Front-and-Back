from django.urls import path
from .views import NotificationListView, NotificationUnreadCountView

urlpatterns = [
    path('', NotificationListView.as_view(), name='notification-list'),
    path('unread/', NotificationUnreadCountView.as_view(), name='unread'),
]
