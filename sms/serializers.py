from rest_framework import serializers
from .models import MessageAnalysis, Feedback

class FeedbackSerializer(serializers.ModelSerializer):
    message_analysis = serializers.PrimaryKeyRelatedField(queryset=MessageAnalysis.objects.all())

    class Meta:
        model = Feedback
        fields = ['id', 'message_analysis', 'was_correct', 'additional_comments', 'created_at']
    def validate(self, data):
        if not data.get('message_analysis'):
            raise serializers.ValidationError({"message_analysis": "This field is required."})
        return data
