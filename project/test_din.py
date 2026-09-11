import os
import django
import json
from django.test import RequestFactory, TestCase
from django.conf import settings
from blood_request.views import register_donor, blood_request_create
from blood_request.models import BloodDonor, BloodRequest
from django.core import mail
from blood_request.utils import generate_unique_din, send_din_email

class DINTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        mail.outbox = []

    def test_manual_utils(self):
        din = generate_unique_din()
        self.assertTrue(din.startswith('DIN-'))
        send_din_email('test@example.com', din, 'donor')
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(din, mail.outbox[0].body)

    def test_donor_registration_and_blood_request(self):
        donor_payload = {
            "name": "Test Donor",
            "blood_group": "A+",
            "phone": "9999999999",
            "email": "testdonor@example.com",
            "city": "Test City",
            "state": "Test State",
            "pin_code": "123456",
            "whatsapp_number": "9999999999",
            "email_notifications": True,
            "available_to_donate": True,
            "consent_given": True
        }
        request = self.factory.post('/api/register/', data=json.dumps(donor_payload), content_type='application/json')
        response = register_donor(request)
        self.assertEqual(response.status_code, 200)
        
        donor = BloodDonor.objects.get(phone="9999999999")
        self.assertIsNotNone(donor.din)
        self.assertTrue(donor.din.startswith('DIN-'))

        req_payload = {
            "city": "Request City",
            "pin_code": "654321",
            "blood_group": "O-",
            "units": "2",
            "address_line_2": "Test Address",
            "contact_person": "Jane Doe",
            "contact_phone": "8888888888",
            "contact_email": "testreq@example.com"
        }
        request = self.factory.post('/api/request/', data=json.dumps(req_payload), content_type='application/json')
        response = blood_request_create(request)
        self.assertEqual(response.status_code, 200)

        breq = BloodRequest.objects.get(contact_phone="8888888888")
        self.assertIsNotNone(breq.din)
        self.assertTrue(breq.din.startswith('DIN-'))

if __name__ == '__main__':
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")
    django.setup()
    from django.test.runner import DiscoverRunner
    test_runner = DiscoverRunner()
    failures = test_runner.run_tests(["test_din"])
