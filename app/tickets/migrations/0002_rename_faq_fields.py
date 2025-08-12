from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='faqknowledgebase',
            old_name='title',
            new_name='question',
        ),
        migrations.RenameField(
            model_name='faqknowledgebase',
            old_name='content',
            new_name='answer',
        ),
    ]
