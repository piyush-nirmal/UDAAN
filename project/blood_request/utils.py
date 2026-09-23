"""
Utility functions for the blood_request app.
"""
from .models import Notification
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import random
import string
import datetime
import uuid
import tempfile
import os
from io import BytesIO
from django.core.files.base import ContentFile
from xhtml2pdf import pisa

def generate_unique_din():
    """Generates a unique Donor Identification Number (DIN)."""
    date_part = datetime.datetime.now().strftime('%Y%m%d')
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"DIN-{date_part}-{random_part}"

def send_din_email(recipient_email, din, record_type='donor'):
    """Sends the generated DIN to the user."""
    if not recipient_email:
        return

    subject = 'Your Udaan Society Identification Number (DIN)'
    
    if record_type == 'donor':
        message = f"Thank you for registering as a blood donor with Udaan Society.\n\nYour Request/Donor Identification Number (DIN) is: {din}\n\nPlease keep this number safe for future tracking.\n\nBest Regards,\nUdaan Society Team"
    else:
        message = f"Thank you for submitting a blood request to Udaan Society.\n\nYour Request Identification Number (DIN) is: {din}\n\nPlease keep this number safe to track your request.\n\nBest Regards,\nUdaan Society Team"

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email='mail@udaansociety.org',
            recipient_list=[recipient_email],
            fail_silently=False,
        )
    except Exception as e:
        print(f"Failed to send email: {e}")


def create_notification(user, message, link=None, actor=None):
    """
    Create a portal notification for a user.
    
    Args:
        user: The User receiving the notification
        message: Notification text
        link: Optional URL to navigate to when clicked
        actor: Optional User who triggered the notification
    """
    return Notification.objects.create(
        user=user,
        message=message,
        link=link or '',
        actor=actor,
    )

def generate_internship_offer_letter(internship_request):
    """Generates an offer letter PDF using weasyprint and saves it to the model."""
    if internship_request.offer_letter:
        return # Already generated

    context = {
        'intern': internship_request,
    }
    
    html_string = render_to_string('pdf/internship_offer_letter.html', context)
    
    # Generate PDF
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html_string.encode("utf-8")), result)
    
    if pdf.err:
        print("Error generating PDF")
        return
        
    pdf_file = result.getvalue()
    
    # Save PDF
    filename = f"offer_letter_{internship_request.name.replace(' ', '_')}_{uuid.uuid4().hex[:6]}.pdf"
    internship_request.offer_letter.save(filename, ContentFile(pdf_file), save=True)

    # Email the PDF
    try:
        from django.core.mail import EmailMessage
        subject = 'Internship Offer Letter - UDAAN Society'
        message = f"Dear {internship_request.name},\n\nCongratulations! We are pleased to offer you an internship at UDAAN Society.\n\nPlease find attached your offer letter. Kindly review the terms and conditions outlined in the annexure.\n\nBest Regards,\nUDAAN Society Team"
        
        email = EmailMessage(
            subject=subject,
            body=message,
            from_email='mail@udaansociety.org',
            to=[internship_request.email],
        )
        email.attach(filename, pdf_file, 'application/pdf')
        email.send(fail_silently=False)
    except Exception as e:
        print(f"Failed to send offer letter email: {e}")


