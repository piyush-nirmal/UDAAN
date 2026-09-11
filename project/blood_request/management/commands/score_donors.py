from django.core.management.base import BaseCommand
from blood_request.models import BloodDonor, Donation

class Command(BaseCommand):
    help = 'Calculates donor scores based on donation history'

    def handle(self, *args, **kwargs):
        donors = BloodDonor.objects.all()
        count = 0
        
        for donor in donors:
            # Calculate total units donated
            # If we had a Donation model, we would aggregate.
            # Since we just added Donation model, we can use it.
            
            donations = Donation.objects.filter(donor=donor)
            total_units = sum(d.units for d in donations)
            
            # Simple scoring logic: 10 points per unit
            # Bonus: 5 points if they have a 'verified' profile (which we don't have explicit field for, assume phone is verified)
            
            new_score = total_units * 10
            
            # Update fields
            donor.donation_count = donations.count() # Count of donation events
            donor.score = new_score
            donor.save()
            
            count += 1
            self.stdout.write(f"Updated {donor.name}: {donor.donation_count} donations, Score: {new_score}")

            if new_score >= 50:
                 self.stdout.write(self.style.SUCCESS(f"  -> STAR DONOR: {donor.name}"))

        self.stdout.write(self.style.SUCCESS(f"Successfully scored {count} donors"))
