import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tms.settings')
django.setup()

from tickets.models import FAQKnowledgeBase

# Get total FAQs
total_faqs = FAQKnowledgeBase.objects.count()
print(f'Total FAQs: {total_faqs}')

# Get published FAQs
published_faqs = FAQKnowledgeBase.objects.filter(is_published=True).count()
print(f'Published FAQs: {published_faqs}')

# Check categories
print('\nCategories with counts:')
for cat, name in FAQKnowledgeBase.CATEGORY_CHOICES:
    count = FAQKnowledgeBase.objects.filter(category=cat, is_published=True).count()
    print(f'{name}: {count}')

# List all FAQs with their categories
print('\nAll FAQs:')
for faq in FAQKnowledgeBase.objects.all():
    status = 'Published' if faq.is_published else 'Draft'
    category = dict(FAQKnowledgeBase.CATEGORY_CHOICES).get(faq.category, faq.category)
    print(f'- {faq.question} (Category: {category}, Status: {status})')
