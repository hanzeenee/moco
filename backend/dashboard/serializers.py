from rest_framework import serializers
from .models import Comment


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'lecture_id', 'author_name', 'content', 'created_at']
        read_only_fields = ['id', 'created_at']