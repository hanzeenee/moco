from django.contrib.auth import authenticate, login
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .serializers import SignupSerializer


@api_view(["POST"])
def signup_api(request):
    serializer = SignupSerializer(data=request.data)

    if serializer.is_valid():
        user = serializer.save()
        return Response(
            {
                "message": "회원가입이 완료되었습니다.",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                },
            },
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

    profile = getattr(user, "profile", None)
    display_name = f"{profile.name}님" if profile and getattr(profile, "name", "") else f"{user.username}님"

    return Response(
        {
            "message": "로그인 성공",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "display_name": display_name,
            },
        },
        status=status.HTTP_200_OK,
    )