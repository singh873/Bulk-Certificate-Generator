from rest_framework import serializers

from .models import Certificate


class RecipientSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    email = serializers.EmailField()
    course = serializers.CharField(max_length=255)


class GenerationJobSerializer(serializers.Serializer):
    recipients = RecipientSerializer(many=True)


class CertificateSerializer(serializers.ModelSerializer):
    download_url = serializers.SerializerMethodField()

    class Meta:
        model = Certificate
        fields = [
            "id",
            "recipient_name",
            "recipient_email",
            "course_name",
            "certificate_number",
            "status",
            "download_url",
            "error_message",
        ]

    def get_download_url(self, obj):
        if obj.file:
            return f"/api/certificates/{obj.id}/download/"
        return None
