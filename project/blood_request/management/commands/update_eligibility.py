from django.core.management.base import BaseCommand
from django.utils import timezone
from blood_request.models import BloodDonor
from datetime import timedelta

class Command(BaseCommand):
    help = 'Checks identifying donors eligible to donate (Last donation > 90 days)'

    def handle(self, *args, **kwargs):
        today = timezone.localdate()
        cutoff_date = today - timedelta(days=90)

        # 1. Donors who have donated before cutoff date OR have never donated (if we treat them as eligible)
        # For this logic, let's look for donors with a last_donation_date that is old enough
        eligible_donors = BloodDonor.objects.filter(last_donation_date__lt=cutoff_date)
        
        # Also include those with NO date? (Assuming new donors are eligible immediately)
        # eligible_donors = eligible_donors | BloodDonor.objects.filter(last_donation_date__isnull=True)

        count = eligible_donors.count()

        if count == 0:
            self.stdout.write(self.style.WARNING(f"No donors found with last donation before {cutoff_date}"))
            return

        self.stdout.write(self.style.SUCCESS(f"Found {count} eligible donors"))

        for donor in eligible_donors:
            # Here we would send an email. For now, we mock it.
            self.stdout.write(f"  [MOCK EMAIL] Sending 'You are eligible' to {donor.name} ({donor.email})")
            
            # Feature Idea: We could update a 'status' field on the donor model too.

        self.stdout.write(self.style.SUCCESS(f"Successfully processed {count} donors"))
