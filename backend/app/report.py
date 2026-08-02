from io import BytesIO
from urllib.request import urlopen

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Image as RLImage
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def generate_pdf_report(patient: dict, visit: dict, image_data: list[dict]) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=18,
    )

    styles = getSampleStyleSheet()
    elements = []

    # Title
    elements.append(Paragraph("Clinic-AI Dental Screening Report", styles["Title"]))
    elements.append(Spacer(1, 0.25 * inch))

    # Patient Information
    patient_data = [
        ["Patient Name", patient.get("name", "N/A")],
        ["Date of Birth", str(patient.get("dob", "N/A"))[:10]],
        ["Gender", str(patient.get("gender", "N/A")).capitalize()],
        ["Contact", patient.get("contact", "N/A")],
    ]
    t = Table(patient_data, colWidths=[2 * inch, 4 * inch])
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
                ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("GRID", (0, 0), (-1, -1), 1, colors.silver),
            ]
        )
    )
    elements.append(Paragraph("Patient Information", styles["Heading2"]))
    elements.append(t)
    elements.append(Spacer(1, 0.25 * inch))

    # Visit Information
    visit_data = [
        ["Visit Date", str(visit.get("date", "N/A"))[:10]],
        ["Complaint", visit.get("complaint", "N/A")],
        ["Notes", visit.get("notes", "N/A")],
    ]
    t2 = Table(visit_data, colWidths=[2 * inch, 4 * inch])
    t2.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
                ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("GRID", (0, 0), (-1, -1), 1, colors.silver),
            ]
        )
    )
    elements.append(Paragraph("Visit Information", styles["Heading2"]))
    elements.append(t2)
    elements.append(Spacer(1, 0.25 * inch))

    # Images and Detections
    elements.append(Paragraph("Images & AI Detections", styles["Heading2"]))
    for item in image_data:
        image_doc = item["image"]
        corrections = item.get("corrections")
        predictions = item.get("predictions")

        # Download image for PDF
        try:
            image_url = image_doc["imageUrl"]
            img_data = BytesIO(urlopen(image_url).read())
            img = RLImage(img_data, width=4 * inch, height=3 * inch)
            elements.append(img)
            elements.append(Spacer(1, 0.1 * inch))
        except Exception:
            elements.append(Paragraph("[Image could not be loaded]", styles["Normal"]))

        # Status
        reviewed = image_doc.get("reviewedAt")
        status_text = "Status: Reviewed by Dentist" if reviewed else "Status: Pending Review"
        elements.append(Paragraph(status_text, styles["Italic"]))
        elements.append(Spacer(1, 0.1 * inch))

        # Detections
        if corrections is not None:
            elements.append(Paragraph("Dentist Corrections:", styles["Heading3"]))
            if not corrections:
                elements.append(Paragraph("No conditions found.", styles["Normal"]))
            else:
                for c in corrections:
                    elements.append(
                        Paragraph(f"• {c['disease_name'].capitalize()}", styles["Normal"])
                    )
        elif predictions is not None:
            elements.append(Paragraph("AI Predictions:", styles["Heading3"]))
            if not predictions:
                elements.append(Paragraph("No conditions detected.", styles["Normal"]))
            else:
                for p in predictions:
                    conf = round(p["confidence"] * 100)
                    elements.append(
                        Paragraph(f"• {p['disease_name'].capitalize()} ({conf}%)", styles["Normal"])
                    )
        else:
            elements.append(Paragraph("No AI analysis available.", styles["Normal"]))

        elements.append(Spacer(1, 0.25 * inch))

    doc.build(elements)
    return buffer.getvalue()
