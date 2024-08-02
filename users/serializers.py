from rest_framework import serializers
from .models import CustomUser, FriendRequest
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate

class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['email', 'password', 'password_confirm']

    def validate(self, data):
        password = data.get('password')
        password_confirm = data.get('password_confirm')
        if password != password_confirm:
            raise serializers.ValidationError("Passwords do not match")
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email')

class FriendRequestSerializer(serializers.ModelSerializer):
    from_user = serializers.StringRelatedField()
    to_user = serializers.StringRelatedField()

    class Meta:
        model = FriendRequest
        fields = ('id', 'from_user', 'to_user', 'created_at', 'status')

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        user = authenticate(email=email, password=password)
        if not user:
            raise serializers.ValidationError('Invalid email or password')
        return data

class SearchSerializer(serializers.Serializer):
    search_keyword = serializers.CharField(required=True)

class FriendRequestActionSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    action = serializers.ChoiceField(choices=['send', 'accept', 'reject'], required=True)

class LogoutSerializer(serializers.Serializer):
    pass
