import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from django.contrib.auth.models import User
from blood_request.models import Appointment

def run():
    with open('debug_output.txt', 'w') as f:
        f.write("--- Debugging Appointments ---\n")
        users = User.objects.all()
        for user in users:
            count = Appointment.objects.filter(staff=user).count()
            f.write(f"User: {user.username} (ID: {user.id}) | Staff: {user.is_staff} | Super: {user.is_superuser} | Appointments: {count}\n")
            if count > 0:
                for appt in Appointment.objects.filter(staff=user):
                    f.write(f"  - {appt.title} ({appt.status})\n")

if __name__ == '__main__':
    run()
