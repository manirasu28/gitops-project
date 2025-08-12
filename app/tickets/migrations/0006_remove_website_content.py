from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('tickets', '0005_fix_roles'),
    ]

    operations = [
        migrations.DeleteModel(
            name='WebsiteContent',
        ),
    ]
