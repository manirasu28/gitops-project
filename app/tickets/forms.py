from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import UserMeta, Ticket, TicketResponse, TicketAction, Media, FAQKnowledgeBase

# Custom user registration form
class CustomerRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

# Custom login form
class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))

# User profile form
class UserProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=255, required=True)
    last_name = forms.CharField(max_length=255, required=True)
    
    class Meta:
        model = UserMeta
        fields = ('first_name', 'last_name', 'gender', 'contact_number', 'location')
    
    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['first_name'].initial = self.instance.first_name
            self.fields['last_name'].initial = self.instance.last_name

# Ticket creation form
class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ('title', 'description', 'category')
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
        }

# Ticket response form
class TicketResponseForm(forms.ModelForm):
    class Meta:
        model = TicketResponse
        fields = ('message',)
        widgets = {
            'message': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Write your response here...'}),
        }

# Ticket action form (for support agents)
class TicketActionForm(forms.ModelForm):
    """Form for recording agent actions on tickets"""
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
    
    action_type = forms.ChoiceField(choices=ACTION_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))
    action_taken = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Brief description of action taken'}), required=False)
    resolution_summary = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Detailed summary of resolution (if applicable)'}), required=False)
    notes = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Add notes about this action (only visible to support and admin)'}), required=False)
    
    class Meta:
        model = TicketAction
        fields = ['action_type', 'action_taken', 'resolution_summary', 'notes']

# Media upload form
class MediaUploadForm(forms.ModelForm):
    class Meta:
        model = Media
        fields = ('file',)
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.ticket = kwargs.pop('ticket', None)
        super(MediaUploadForm, self).__init__(*args, **kwargs)
    
    def save(self, commit=True):
        instance = super(MediaUploadForm, self).save(commit=False)
        if self.user:
            instance.user = self.user
        if self.ticket:
            instance.ticket = self.ticket
            
        # Determine file type
        file_name = instance.file.name
        file_extension = file_name.split('.')[-1].lower()
        
        # Set file type based on extension
        if file_extension in ['jpg', 'jpeg', 'png', 'gif']:
            instance.file_type = 'image'
        elif file_extension in ['pdf', 'doc', 'docx', 'txt']:
            instance.file_type = 'document'
        else:
            instance.file_type = 'other'
            
        if commit:
            instance.save()
        return instance

# FAQ form
class FAQForm(forms.ModelForm):
    class Meta:
        model = FAQKnowledgeBase
        fields = ('question', 'answer', 'category', 'related_ticket_category', 'is_published', 'order')
        widgets = {
            'answer': forms.Textarea(attrs={'rows': 5, 'class': 'form-control'}),
            'question': forms.TextInput(attrs={'class': 'form-control'}),
        }
