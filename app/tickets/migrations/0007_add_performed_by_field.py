from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings

class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tickets', '0006_remove_website_content'),
    ]

    operations = [
        migrations.AddField(
            model_name='ticketaction',
            name='performed_by',
            field=models.ForeignKey(
                to=settings.AUTH_USER_MODEL,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='ticket_actions',
                null=True  # We need this to be nullable initially
            ),
        ),
    ]
