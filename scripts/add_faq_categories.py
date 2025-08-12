import os
import django

# Set up Django environment first
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tms.settings')
django.setup()

# Now import models after Django is configured
from django.contrib.auth.models import User
from tickets.models import FAQKnowledgeBase, TicketCategory

# Get admin user for created_by field
admin_user = User.objects.filter(is_superuser=True).first()

if not admin_user:
    print("No admin user found. Please create an admin user first.")
    exit(1)

# Get a ticket category for related_ticket_category field
ticket_category = TicketCategory.objects.first()

# Define new FAQs for different categories
new_faqs = [
    # Account & Profile FAQs
    {
        "question": "How do I update my profile information?",
        "answer": "To update your profile information, log in to your account and click on your username in the top right corner. Select 'Profile' from the dropdown menu. On your profile page, click the 'Edit Profile' button to make changes to your personal information.",
        "category": "account",
        "order": 1,
    },
    {
        "question": "Can I change my username?",
        "answer": "Yes, you can change your username. Go to your profile settings by clicking on your current username in the top right corner and selecting 'Profile'. Then click 'Edit Profile' and update your username in the form provided. Please note that your username must be unique.",
        "category": "account",
        "order": 2,
    },
    {
        "question": "How do I enable two-factor authentication?",
        "answer": "To enable two-factor authentication (2FA), go to your account settings and select the 'Security' tab. Click on 'Enable Two-Factor Authentication' and follow the instructions to set it up using an authenticator app on your mobile device.",
        "category": "account",
        "order": 3,
    },
    
    # Tickets & Support FAQs
    {
        "question": "What information should I include in my support ticket?",
        "answer": "When creating a support ticket, please include: a clear description of the issue, steps to reproduce the problem, any error messages you received, and relevant screenshots if possible. The more details you provide, the faster our team can assist you.",
        "category": "tickets",
        "order": 1,
        "related_ticket_category": ticket_category
    },
    {
        "question": "How long does it take to get a response to my ticket?",
        "answer": "Our support team typically responds to tickets within 24 hours during business days. Priority tickets or critical issues may receive faster responses. You'll receive email notifications when there are updates to your ticket.",
        "category": "tickets",
        "order": 2,
    },
    {
        "question": "Can I update a ticket after submitting it?",
        "answer": "Yes, you can update your ticket after submission. Simply log in to your account, go to 'My Tickets', find the ticket you want to update, and click on it. You can add additional information or attachments by posting a reply to the ticket thread.",
        "category": "tickets",
        "order": 3,
    },
    
    # Billing & Payments FAQs
    {
        "question": "What payment methods do you accept?",
        "answer": "We accept major credit cards (Visa, MasterCard, American Express), PayPal, and bank transfers for annual subscriptions. All payments are processed securely through our payment gateway with industry-standard encryption.",
        "category": "billing",
        "order": 1,
    },
    {
        "question": "How do I view my billing history?",
        "answer": "To view your billing history, log in to your account and go to 'Account Settings'. Select the 'Billing' tab to see a list of all your past invoices and payment receipts. You can download or print these documents for your records.",
        "category": "billing",
        "order": 2,
    },
    {
        "question": "Can I get a refund if I'm not satisfied?",
        "answer": "We offer a 30-day money-back guarantee for new subscriptions. If you're not satisfied with our service within the first 30 days, contact our support team to request a refund. Please note that refunds for partial months or special circumstances are handled on a case-by-case basis.",
        "category": "billing",
        "order": 3,
    },
    
    # Technical Issues FAQs
    {
        "question": "Why is the system running slowly?",
        "answer": "System performance can be affected by several factors including your internet connection, browser cache, or high system load. Try clearing your browser cache, using a different browser, or accessing the system during off-peak hours. If the issue persists, please contact our support team.",
        "category": "technical",
        "order": 1,
    },
    {
        "question": "How do I troubleshoot login issues?",
        "answer": "If you're having trouble logging in, first ensure you're using the correct email and password. Try resetting your password using the 'Forgot Password' link. Clear your browser cookies and cache, or try using a different browser. If you still can't log in, contact our support team for assistance.",
        "category": "technical",
        "order": 2,
    },
    {
        "question": "What browsers are supported?",
        "answer": "Our system supports the latest versions of Chrome, Firefox, Safari, and Edge. For the best experience, we recommend keeping your browser updated to the latest version. Internet Explorer is not fully supported and may cause display or functionality issues.",
        "category": "technical",
        "order": 3,
    },
]

# Add new FAQs
for faq_data in new_faqs:
    # Check if FAQ already exists
    existing = FAQKnowledgeBase.objects.filter(question=faq_data["question"]).first()
    
    if not existing:
        # Create new FAQ
        FAQKnowledgeBase.objects.create(
            question=faq_data["question"],
            answer=faq_data["answer"],
            category=faq_data["category"],
            order=faq_data["order"],
            related_ticket_category=faq_data.get("related_ticket_category"),
            created_by=admin_user,
            is_published=True
        )
        print(f"Added FAQ: {faq_data['question']}")
    else:
        print(f"FAQ already exists: {faq_data['question']}")

print("\nFAQ categories updated successfully!")
