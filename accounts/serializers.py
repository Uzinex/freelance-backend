import random
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db.models import Q
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from twilio.rest import Client

from .models import PasswordResetCode

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'phone', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    identifier = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        identifier = attrs.get('identifier')
        password = attrs.get('password')
        user = User.objects.filter(
            Q(username=identifier) | Q(email=identifier) | Q(phone=identifier)
        ).first()
        if user is None or not user.check_password(password):
            raise serializers.ValidationError('Invalid credentials')
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }


class PasswordResetRequestSerializer(serializers.Serializer):
    identifier = serializers.CharField()

    def validate(self, attrs):
        identifier = attrs.get('identifier')
        user = User.objects.filter(Q(email=identifier) | Q(phone=identifier)).first()
        if user is None:
            raise serializers.ValidationError('User not found')
        attrs['user'] = user
        attrs['identifier'] = identifier
        return attrs

    def create(self, validated_data):
        user = validated_data['user']
        identifier = validated_data['identifier']
        code = str(random.randint(100000, 999999))
        PasswordResetCode.objects.create(user=user, code=code)
        if '@' in identifier:
            send_mail(
                'Password Reset Code',
                f'Your password reset code is {code}',
                getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@example.com'),
                [identifier],
                fail_silently=True,
            )
        else:
            account_sid = getattr(settings, 'TWILIO_ACCOUNT_SID', None)
            auth_token = getattr(settings, 'TWILIO_AUTH_TOKEN', None)
            from_number = getattr(settings, 'TWILIO_FROM_NUMBER', None)
            if account_sid and auth_token and from_number:
                client = Client(account_sid, auth_token)
                client.messages.create(body=f'Your password reset code is {code}', from_=from_number, to=identifier)
            else:
                print(f'SMS to {identifier}: {code}')
        return validated_data


class PasswordResetConfirmSerializer(serializers.Serializer):
    identifier = serializers.CharField()
    code = serializers.CharField()
    new_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        identifier = attrs.get('identifier')
        user = User.objects.filter(Q(email=identifier) | Q(phone=identifier)).first()
        if user is None:
            raise serializers.ValidationError('User not found')
        reset_code = (
            PasswordResetCode.objects.filter(user=user, code=attrs.get('code'), is_used=False)
            .order_by('-created_at')
            .first()
        )
        if reset_code is None or not reset_code.is_valid():
            raise serializers.ValidationError('Invalid or expired code')
        attrs['user'] = user
        attrs['reset_code'] = reset_code
        return attrs

    def create(self, validated_data):
        user = validated_data['user']
        reset_code = validated_data['reset_code']
        new_password = validated_data['new_password']
        user.set_password(new_password)
        user.save()
        reset_code.is_used = True
        reset_code.save()
        return {'detail': 'Password reset successful'}
