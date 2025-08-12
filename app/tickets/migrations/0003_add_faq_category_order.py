from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0002_rename_faq_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='faqknowledgebase',
            name='category',
            field=models.CharField(choices=[('general', 'General Information'), ('account', 'Account & Profile'), ('tickets', 'Tickets & Support'), ('billing', 'Billing & Payments'), ('technical', 'Technical Issues')], default='general', max_length=20),
        ),
        migrations.AddField(
            model_name='faqknowledgebase',
            name='is_published',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='faqknowledgebase',
            name='order',
            field=models.PositiveIntegerField(default=0, help_text='Display order (lower numbers shown first)'),
        ),
    ]
