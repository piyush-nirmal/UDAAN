# Blood Donation API Update

Added working Django endpoints for the Blood Donation page:

- `POST /api/ngo/register/`
- `POST /api/bloodbank/register/`
- `POST /api/camp-rsvp/`
- `POST /api/alerts/subscribe/`

Database models and migration `0058_blood_donation_partner_models.py` are included.

After installing dependencies, run:

```bash
python manage.py migrate
python manage.py runserver
```

The frontend already posts JSON to these endpoints and CSRF tokens are included.
