from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver

# Role model for user permissions
class Role(models.Model):
    AVAILABLE_PERMISSIONS = [
        ('view_all_tickets', 'Can view all tickets'),
        ('edit_all_tickets', 'Can edit all tickets'),
        ('assign_tickets', 'Can assign tickets to agents'),
        ('view_assigned_tickets', 'Can view assigned tickets'),
        ('respond_to_tickets', 'Can respond to tickets'),
        ('close_tickets', 'Can close tickets'),
        ('manage_users', 'Can manage users'),
        ('manage_categories', 'Can manage ticket categories'),
        ('manage_faq', 'Can manage FAQ/Knowledge Base'),
    ]
    
    name = models.CharField(max_length=100)
    permissions = models.TextField(blank=True, null=True, help_text="Comma-separated list of permissions")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
        
    def get_permissions(self):
        """Returns the list of permissions for this role"""
        if not self.permissions:
            return []
        return [p.strip() for p in self.permissions.split(',') if p.strip()]
    
    def has_permission(self, permission):
        """Check if this role has the specified permission"""
        if not self.permissions:
            return False
        permissions = self.get_permissions()
        # Admin role has all permissions
        if self.name.lower() == 'admin':
            return True
        return permission in permissions
    
    def set_permissions(self, permissions_list):
        """Set permissions from a list of permission strings"""
        if not permissions_list:
            self.permissions = ''
        else:
            self.permissions = ','.join(permissions_list)
            
    def set_permission(self, permission_name, has_permission=True):
        """Add or remove a permission"""
        permissions = self.get_permissions()
        
        # Check if the permission is valid
        valid_permissions = [p[0] for p in self.AVAILABLE_PERMISSIONS]
        if permission_name not in valid_permissions:
            raise ValueError(f"Invalid permission: {permission_name}")
            
        if has_permission and permission_name not in permissions:
            permissions.append(permission_name)
        elif not has_permission and permission_name in permissions:
            permissions.remove(permission_name)
            
        self.permissions = ",".join(permissions)
        self.save()

# User metadata model
class UserMeta(models.Model):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_meta')
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    full_name = models.CharField(max_length=510, blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    contact_number = models.CharField(max_length=20, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)
    is_profile_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Update full name when first/last name is saved
        if self.first_name and self.last_name:
            self.full_name = f"{self.first_name} {self.last_name}"
        super(UserMeta, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username}'s profile"

# Create UserMeta instance when a User is created
@receiver(post_save, sender=User)
def create_user_meta(sender, instance, created, **kwargs):
    if created:
        # Get the default user role or create it if it doesn't exist
        user_role, _ = Role.objects.get_or_create(name='user')
        UserMeta.objects.create(user=instance, role=user_role)

# Ticket category model
class TicketCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Ticket Categories"

# Ticket model
class Ticket(models.Model):
    """Model for storing ticket information"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    # Relationship fields
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tickets')
    assigned_to = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='assigned_tickets')
    category = models.ForeignKey(TicketCategory, on_delete=models.PROTECT, related_name='tickets')
    
    # Content fields
    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    
    # Timestamp fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"#{self.id} - {self.title}"
        
    @property
    def ticket_id(self):
        """Return a formatted ticket id for display purposes"""
        return f"TKT-{self.id:04d}"
    
    def get_absolute_url(self):
        return reverse('ticket_detail', args=[str(self.id)])

# Ticket response model
class TicketResponse(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='responses')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Response to {self.ticket.title} by {self.user.username}"

# Ticket action model
class TicketAction(models.Model):
    """Model for storing support agent actions"""
    ACTION_CHOICES = [
        ('review', 'Reviewed ticket'),
        ('update', 'Updated ticket information'),
        ('escalate', 'Escalated to higher support'),
        ('assign', 'Assigned/reassigned ticket'),
        ('status_change', 'Changed ticket status'),
        ('note', 'Added internal note'),
        ('reset_password', 'Reset user password'),
        ('other', 'Other action'),
    ]
    
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='actions')
    performed_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ticket_actions', null=True)
    action_type = models.CharField(max_length=20, choices=ACTION_CHOICES, default='note')
    action_taken = models.CharField(max_length=255, blank=True, null=True, help_text="Brief description of action taken")
    resolution_summary = models.TextField(blank=True, null=True, help_text="Detailed summary of resolution")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    
    def __str__(self):
        return f"{self.get_action_type_display()} by {self.performed_by.username} on {self.created_at.strftime('%Y-%m-%d %H:%M')}"

# FAQ/Knowledge Base model
class FAQKnowledgeBase(models.Model):
    CATEGORY_CHOICES = [
        ('general', 'General Information'),
        ('account', 'Account & Profile'),
        ('tickets', 'Tickets & Support'),
        ('billing', 'Billing & Payments'),
        ('technical', 'Technical Issues'),
    ]
    
    question = models.CharField(max_length=255)
    answer = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='general')
    order = models.PositiveIntegerField(default=0, help_text="Display order (lower numbers shown first)")
    related_ticket_category = models.ForeignKey(TicketCategory, on_delete=models.SET_NULL, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.question
    
    class Meta:
        verbose_name = "FAQ Item"
        verbose_name_plural = "FAQ Knowledge Base"
        ordering = ['category', 'order', 'question']

# Media model for file uploads
class Media(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='media', null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='media')
    file = models.FileField(upload_to='uploads/')
    file_type = models.CharField(max_length=50)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Media"
    
    def __str__(self):
        return f"File uploaded by {self.user.username} at {self.uploaded_at.strftime('%Y-%m-%d %H:%M')}"
