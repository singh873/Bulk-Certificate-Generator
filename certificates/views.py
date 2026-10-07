from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import FileResponse

from .models import Certificate, GenerationJob
from .serializers import CertificateSerializer, GenerationJobSerializer
from .tasks import generate_certificate


class GenerationJobCreateView(APIView):
    def post(self, request):
        serializer = GenerationJobSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        recipients = serializer.validated_data["recipients"]
        job = GenerationJob.objects.create(total_count=len(recipients))

        for index, recipient in enumerate(recipients, start=1):
            certificate = Certificate.objects.create(job=job, recipient_name=recipient["name"], recipient_email=recipient["email"], course_name=recipient["course"], certificate_number=f"CERT-{job.id:05d}-{index:05d}")
            generate_certificate.delay(certificate.id)

        return Response({"job_id": job.id, "status": job.status, "total_count": job.total_count}, status=status.HTTP_201_CREATED)


class GenerationJobStatusView(APIView):
    def get(self, request, job_id):
        try:
            job = GenerationJob.objects.get(id=job_id)
        except GenerationJob.DoesNotExist:
            return Response({"error": "Job not found."}, status=status.HTTP_404_NOT_FOUND)

        pending_count = job.total_count - job.success_count - job.failed_count
        return Response({"job_id": job.id, "status": job.status, "total_count": job.total_count, "success_count": job.success_count, "failed_count": job.failed_count, "pending_count": pending_count})


class JobCertificatesView(APIView):
    def get(self, request, job_id):
        try:
            job = GenerationJob.objects.get(id=job_id)
        except GenerationJob.DoesNotExist:
            return Response({"error": "Job not found."}, status=status.HTTP_404_NOT_FOUND)

        certificates = job.certificates.all()
        serializer = CertificateSerializer(certificates, many=True)
        return Response({"job_id": job.id, "certificates": serializer.data})


class CertificateDownloadView(APIView):
    def get(self, request, certificate_id):
        try:
            certificate = Certificate.objects.get(id=certificate_id)
        except Certificate.DoesNotExist:
            return Response({"error": "Certificate not found."}, status=status.HTTP_404_NOT_FOUND)

        if certificate.status != Certificate.Status.COMPLETED:
            return Response({"error": "Certificate is not ready for download."}, status=status.HTTP_400_BAD_REQUEST)

        if not certificate.file:
            return Response({"error": "Certificate file not found."}, status=status.HTTP_404_NOT_FOUND)

        return FileResponse(certificate.file.open("rb"), content_type="application/pdf", as_attachment=True, filename=f"{certificate.certificate_number}.pdf")