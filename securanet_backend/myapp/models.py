from django.db import models

# Create youfrom django.db import models

class FileChangeLog(models.Model):
    file_path = models.CharField(max_length=500)
    change_type = models.CharField(max_length=20)
    suspicious = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.change_type.upper()}: {self.file_path}"

