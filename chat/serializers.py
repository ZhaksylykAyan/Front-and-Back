from rest_framework import serializers
from chat.models import Chat, Message, UserStatus
from users.models import CustomUser
from profiles.models import StudentProfile, SupervisorProfile, DeanOfficeProfile

class ProfileSerializer(serializers.Serializer):
    first_name = serializers.CharField(allow_null=True)
    last_name = serializers.CharField(allow_null=True)
    photo = serializers.ImageField(allow_null=True)

class UserSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'role', 'profile']

    def get_profile(self, obj):
        if obj.role == "Student" and hasattr(obj, "student_profile"):
            return {
                "first_name": obj.student_profile.first_name,
                "last_name": obj.student_profile.last_name,
                "photo": obj.student_profile.photo.url if obj.student_profile.photo else None
            }
        elif obj.role == "Supervisor" and hasattr(obj, "supervisor_profile"):
            return {
                "first_name": obj.supervisor_profile.first_name,
                "last_name": obj.supervisor_profile.last_name,
                "photo": obj.supervisor_profile.photo.url if obj.supervisor_profile.photo else None
            }
        elif obj.role == "Dean Office" and hasattr(obj, "dean_office_profile"):
            return {
                "first_name": obj.dean_office_profile.first_name,
                "last_name": obj.dean_office_profile.last_name,
                "photo": obj.dean_office_profile.photo.url if obj.dean_office_profile.photo else None
            }
        return None


class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'sender', 'content', 'timestamp', 'is_read']


class ChatSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True)

    class Meta:
        model = Chat
        fields = ['id', 'participants', 'created_at']


class UserStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserStatus
        fields = ['is_online', 'last_seen']
