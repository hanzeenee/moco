from django.contrib.auth import authenticate, login, logout
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .serializers import SignupSerializer


def user_payload(user):
    profile = getattr(user, "profile", None)
    display_name = profile.name if profile and getattr(profile, "name", "") else user.username
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "display_name": display_name,
    }


@api_view(["POST"])
def signup_api(request):
    serializer = SignupSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response(
            {"message": "회원가입이 완료되었습니다.", "user": user_payload(user)},
            status=status.HTTP_201_CREATED,
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def login_api(request):
    username = request.data.get("username", "").strip()
    password = request.data.get("password", "")

    if not username or not password:
        return Response(
            {"detail": "아이디와 비밀번호를 입력하세요."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = authenticate(request, username=username, password=password)
    if user is None:
        return Response(
            {"detail": "아이디 또는 비밀번호가 올바르지 않습니다."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    login(request, user)
    return Response(
        {"message": "로그인 성공", "user": user_payload(user)},
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
def logout_api(request):
    logout(request)
    return Response({"message": "로그아웃 성공"}, status=status.HTTP_200_OK)


@api_view(["GET"])
def me_api(request):
    if not request.user.is_authenticated:
        return Response({"authenticated": False}, status=status.HTTP_200_OK)
    return Response(
        {"authenticated": True, "user": user_payload(request.user)},
        status=status.HTTP_200_OK,
    )
