from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("username", "email", "phone", "password", "role")
        extra_kwargs = {
            "email": {"required": False},
            "phone": {"required": False},
            "role": {"required": False},
        }

    def create(self, validated_data):
        return User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email"),
            phone=validated_data.get("phone"),
            role=validated_data.get("role", "freelancer"),
            password=validated_data["password"],
        )
