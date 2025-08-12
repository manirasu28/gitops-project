import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tms.settings')
django.setup()

from tickets.models import TicketCategory, FAQKnowledgeBase
from django.contrib.auth.models import User

# Get admin user for creating FAQs
admin_user = User.objects.get(username='admin')

# Create sample ticket categories
categories = [
    {
        'name': 'Technical Support',
        'description': 'Issues related to software or hardware technical problems'
    },
    {
        'name': 'Billing',
        'description': 'Questions about billing, invoices, and payments'
    },
    {
        'name': 'Account Management',
        'description': 'Help with account settings, profile updates, and access issues'
    },
    {
        'name': 'Feature Requests',
        'description': 'Suggestions and requests for new features or improvements'
    },
    {
        'name': 'Bug Reports',
        'description': 'Report bugs or unexpected behavior in our products'
    },
]

# Create the categories if they don't exist
for category_data in categories:
    category, created = TicketCategory.objects.get_or_create(
        name=category_data['name'],
        defaults={'description': category_data['description']}
    )
    if created:
        print(f"Created category: {category.name}")
    else:
        print(f"Category {category.name} already exists")

# Create sample FAQs
faqs = [
    {
        'title': 'How do I reset my password?',
        'content': 'To reset your password, click on the "Forgot Password" link on the login page. You will receive an email with instructions to reset your password.',
        'category_name': 'Account Management'
    },
    {
        'title': 'How can I update my billing information?',
        'content': 'You can update your billing information by going to your account settings and selecting the "Billing" tab. From there, you can modify your payment method and billing details.',
        'category_name': 'Billing'
    },
    {
        'title': 'What file formats can I upload as attachments?',
        'content': 'Our system supports various file formats including images (JPG, PNG, GIF), documents (PDF, DOC, DOCX, TXT), and other common file types. The maximum file size is 10MB per attachment.',
        'category_name': 'Technical Support'
    },
    {
        'title': 'How do I create a new support ticket?',
        'content': 'After logging in, navigate to your dashboard and click on "Create New Ticket". Fill in the required information including title, category, and description of your issue. You can also attach files if needed.',
        'category_name': 'Technical Support'
    },
    {
        'title': 'What happens after I submit a ticket?',
        'content': 'After submitting a ticket, it will be assigned to an appropriate support agent who will review your issue. You will receive notifications for any updates to your ticket, and you can check its status anytime from your dashboard.',
        'category_name': 'Technical Support'
    },
]

# Create the FAQs if they don't exist
for faq_data in faqs:
    # Get the related category
    try:
        category = TicketCategory.objects.get(name=faq_data['category_name'])
        
        # Check if FAQ exists
        existing_faq = FAQKnowledgeBase.objects.filter(question=faq_data['title']).first()
        if not existing_faq:
            faq = FAQKnowledgeBase.objects.create(
                question=faq_data['title'],
                answer=faq_data['content'],
                related_ticket_category=category,
                created_by=admin_user,
                category='general'  # Default category
            )
            print(f"Created FAQ: {faq.question}")
        else:
            print(f"FAQ {faq_data['title']} already exists")
    except TicketCategory.DoesNotExist:
        print(f"Category {faq_data['category_name']} not found. Skipping FAQ creation.")

print("\nSample data creation completed.")
