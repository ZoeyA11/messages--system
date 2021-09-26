from rest_framework import serializers

from .models import Message


class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.SlugRelatedField(many=False, slug_field="username", read_only=True)
    reciever = serializers.SlugRelatedField(many=False, slug_field="username", read_only=True)

    class Meta:
        model = Message
        fields = '__all__'
