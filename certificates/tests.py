from unittest.mock import patch

from django.test import TestCase
from rest_framework.test import APIClient

from certificates.models import Certificate, GenerationJob


class CertificateGenerationTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_create_generation_job(self):
        data = {"recipients": [{"name": "Rahul Kumar", "email": "rahul@gmail.com", "course": "Python Backend Development"}, {"name": "Amit Sharma", "email": "amit@gmail.com", "course": "Python Backend Development"}]}
        response = self.client.post("/api/jobs/", data, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["total_count"], 2)
        job = GenerationJob.objects.get(id=response.data["job_id"])
        self.assertEqual(job.total_count, 2)
        self.assertEqual(job.certificates.count(), 2)

    def test_invalid_recipient_data(self):
        data = {"recipients": [{"name": "", "email": "invalid-email", "course": ""}]}
        response = self.client.post("/api/jobs/", data, format="json")
        self.assertEqual(response.status_code, 400)

    def test_job_status(self):
        job = GenerationJob.objects.create(total_count=3, success_count=2, failed_count=1, status=GenerationJob.Status.PARTIALLY_COMPLETED)
        response = self.client.get(f"/api/jobs/{job.id}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["total_count"], 3)
        self.assertEqual(response.data["success_count"], 2)
        self.assertEqual(response.data["failed_count"], 1)
        self.assertEqual(response.data["pending_count"], 0)

    @patch("certificates.tasks.generate_certificate_pdf")
    def test_individual_certificate_failure(self, mock_generate):
        job = GenerationJob.objects.create(total_count=2)
        certificate1 = Certificate.objects.create(job=job, recipient_name="Rahul Kumar", recipient_email="rahul@gmail.com", course_name="Python Backend Development", certificate_number="TEST-00001")
        certificate2 = Certificate.objects.create(job=job, recipient_name="Amit Sharma", recipient_email="amit@gmail.com", course_name="Python Backend Development", certificate_number="TEST-00002")
        mock_generate.side_effect = [Exception("PDF generation failed"), None]
        from certificates.tasks import generate_certificate
        try:
            generate_certificate(certificate1.id)
        except Exception:
            pass
        certificate1.refresh_from_db()
        self.assertEqual(certificate1.status, Certificate.Status.FAILED)
        self.assertIsNotNone(certificate1.error_message)