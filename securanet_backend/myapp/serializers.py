from rest_framework import serializers

class MessageInputSerializer(serializers.Serializer):
    message = serializers.Charfield()
