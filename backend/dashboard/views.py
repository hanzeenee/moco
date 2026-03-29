from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import NavLink, Lecture, Event, Comment
from .serializers import CommentSerializer


@ensure_csrf_cookie
def dashboard_home(request):
    return render(request, "home.html")


def dashboard_data(request):
    nav_links = list(NavLink.objects.values())
    lectures = list(Lecture.objects.values())
    events = list(Event.objects.values())

    data = {
        "nav_links": nav_links,
        "lectures": lectures,
        "events": events,
    }

    return JsonResponse(data)


@api_view(["GET", "POST"])
def comments_api(request):
    if request.method == "GET":
        lecture_id = request.GET.get("lecture_id")

        if not lecture_id:
            return Response(
                {"detail": "lecture_id is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            lecture_id = int(lecture_id)
        except (TypeError, ValueError):
            return Response(
                {"detail": "lecture_id must be an integer."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not Lecture.objects.filter(id=lecture_id).exists():
            return Response(
                {"detail": "Lecture not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        comments = Comment.objects.filter(lecture_id=lecture_id)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    if request.method == "POST":
        lecture_id = request.data.get("lecture_id")

        if not lecture_id:
            return Response(
                {"detail": "lecture_id is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            lecture_id = int(lecture_id)
        except (TypeError, ValueError):
            return Response(
                {"detail": "lecture_id must be an integer."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not Lecture.objects.filter(id=lecture_id).exists():
            return Response(
                {"detail": "Lecture not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = CommentSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(lecture_id=lecture_id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)