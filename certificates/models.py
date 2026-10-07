from django.db import models


class GenerationJob(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        PROCESSING = "PROCESSING", "Processing"
        COMPLETED = "COMPLETED", "Completed"
        PARTIALLY_COMPLETED = "PARTIALLY_COMPLETED", "Partially Completed"
        FAILED = "FAILED", "Failed"

    status = models.CharField(max_length=30, choices=Status.choices, default=Status.PENDING)
    total_count = models.PositiveIntegerField(default=0)
    success_count = models.PositiveIntegerField(default=0)
    failed_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Job #{self.id} - {self.status}"


class Certificate(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        PROCESSING = "PROCESSING", "Processing"
        COMPLETED = "COMPLETED", "Completed"
        FAILED = "FAILED", "Failed"

    job = models.ForeignKey(GenerationJob, on_delete=models.CASCADE, related_name="certificates")
    recipient_name = models.CharField(max_length=255)
    recipient_email = models.EmailField()
    course_name = models.CharField(max_length=255)
    certificate_number = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    file = models.FileField(upload_to="certificates/", null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.recipient_name} - {self.status}"
