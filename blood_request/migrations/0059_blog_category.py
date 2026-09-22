from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blood_request', '0058_blood_donation_partner_models'),
    ]

    operations = [
        migrations.AddField(
            model_name='blog',
            name='category',
            field=models.CharField(
                choices=[
                    ('blog', 'Blog'),
                    ('water', 'Water'),
                    ('education', 'Education'),
                ],
                default='blog',
                max_length=20,
            ),
        ),
    ]
