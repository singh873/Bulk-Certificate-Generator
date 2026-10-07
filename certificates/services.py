from io import BytesIO

from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas


def generate_certificate_pdf(certificate):
    buffer = BytesIO()

    page_width, page_height = landscape(A4)
    pdf = canvas.Canvas(buffer, pagesize=(page_width, page_height))

    pdf.setFont("Helvetica-Bold", 32)
    pdf.drawCentredString(page_width / 2, page_height - 120, "CERTIFICATE OF COMPLETION")

    pdf.setFont("Helvetica", 18)
    pdf.drawCentredString(
        page_width / 2, page_height - 190, "This certificate is proudly presented to"
    )

    pdf.setFont("Helvetica-Bold", 28)
    pdf.drawCentredString(page_width / 2, page_height - 250, certificate.recipient_name)

    pdf.setFont("Helvetica", 18)
    pdf.drawCentredString(
        page_width / 2, page_height - 310, f"for successfully completing {certificate.course_name}"
    )

    pdf.setFont("Helvetica", 14)
    pdf.drawCentredString(
        page_width / 2, 100, f"Certificate No: {certificate.certificate_number}"
    )

    pdf.save()

    buffer.seek(0)

    return buffer
