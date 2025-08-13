from django.db import models

class MessageAnalysis(models.Model):
    original_message = models.TextField()
    result = models.CharField(max_length=10)  # Either 'Threat' or 'Safe'
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.result}: {self.original_message[:30]}"

class Feedback(models.Model):
    message_analysis = models.ForeignKey(MessageAnalysis, on_delete=models.CASCADE, related_name='feedbacks')
    was_correct = models.BooleanField()  # True if user agrees with result
    additional_comments = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Feedback on {self.message_analysis.id} - Correct: {self.was_correct}"
