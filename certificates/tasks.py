from celery import shared_task
from django.core.files.base import ContentFile

from .models import Certificate, GenerationJob
from .services import generate_certificate_pdf


def update_job_status(job):
    certificates = job.certificates.all()
    total = certificates.count()
    success = certificates.filter(status=Certificate.Status.COMPLETED).count()
    failed = certificates.filter(status=Certificate.Status.FAILED).count()
    pending = total - success - failed
    job.success_count = success
    job.failed_count = failed

    if pending > 0:
        job.status = GenerationJob.Status.PROCESSING
    elif failed == 0:
        job.status = GenerationJob.Status.COMPLETED
    elif success > 0:
        job.status = GenerationJob.Status.PARTIALLY_COMPLETED
    else:
        job.status = GenerationJob.Status.FAILED

    job.save(update_fields=["status", "success_count", "failed_count"])


@shared_task
def generate_certificate(certificate_id):
    certificate = Certificate.objects.get(id=certificate_id)
    certificate.status = Certificate.Status.PROCESSING
    certificate.save(update_fields=["status"])
    update_job_status(certificate.job)

    try:
        pdf = generate_certificate_pdf(certificate)
        certificate.file.save(f"{certificate.certificate_number}.pdf", ContentFile(pdf.getvalue()), save=False)
        certificate.status = Certificate.Status.COMPLETED
        certificate.error_message = None
        certificate.save(update_fields=["file", "status", "error_message"])
        update_job_status(certificate.job)
        return {"certificate_id": certificate.id, "status": certificate.status}

    except Exception as error:
        certificate.status = Certificate.Status.FAILED
        certificate.error_message = str(error)
        certificate.save(update_fields=["status", "error_message"])
        update_job_status(certificate.job)
        raise