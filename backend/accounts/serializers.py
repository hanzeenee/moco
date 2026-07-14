import re
from datetime import datetime

from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Profile


class SignupSerializer(serializers.Serializer):
    email = serializers.EmailField()
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, min_length=4)
    password_confirm = serializers.CharField(write_only=True, min_length=4)
    name = serializers.CharField(max_length=50)
    birth = serializers.CharField(max_length=6)
    phone = serializers.CharField(max_length=11)

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("이미 사용 중인 아이디입니다.")
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("이미 사용 중인 이메일입니다.")
        return value

    def validate_name(self, value):
        if not re.fullmatch(r"[가-힣]+", value):
            raise serializers.ValidationError("이름은 한글만 입력할 수 있습니다.")
        return value

    def validate_birth(self, value):
        if not re.fullmatch(r"\d{6}", value):
            raise serializers.ValidationError("생년월일 6자리를 숫자로 입력하세요.")

        yy = int(value[:2])
        mm = int(value[2:4])
        dd = int(value[4:6])
        current_two_digit_year = datetime.now().year % 100
        year = 2000 + yy if yy <= current_two_digit_year else 1900 + yy

        try:
            datetime(year, mm, dd)
        except ValueError as exc:
            raise serializers.ValidationError("올바른 생년월일 6자리 형식이 아닙니다.") from exc

        return value

    def validate_phone(self, value):
        if "-" in value:
            raise serializers.ValidationError("휴대폰 번호는 '-' 없이 입력하세요.")

        if not re.fullmatch(r"01[016789]\d{7,8}", value):
            raise serializers.ValidationError("올바른 휴대폰 번호 형식이 아닙니다. 예: 01012345678")

        return value

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError({
                "password_confirm": "비밀번호가 일치하지 않습니다."
            })
        return attrs

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
        )
        Profile.objects.create(
            user=user,
            name=validated_data["name"],
            birth=validated_data["birth"],
            phone=validated_data["phone"],
        )
        return user
