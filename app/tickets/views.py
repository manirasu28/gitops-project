from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, views as auth_views
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse, HttpResponseForbidden
from .models import Role, UserMeta, TicketCategory, Ticket, TicketResponse, TicketAction, FAQKnowledgeBase, Media
from .forms import (
    CustomerRegistrationForm, CustomLoginForm, UserProfileForm, TicketForm,
    TicketResponseForm, TicketActionForm, MediaUploadForm, FAQForm
)
from django.core.paginator import Paginator
from django.utils import timezone

# Landing page view
def home(request):
    # Get 5 published FAQs for the home page preview
    faqs = FAQKnowledgeBase.objects.filter(is_published=True).order_by('category', 'order', 'question')[:5]
    return render(request, 'tickets/home.html', {'faqs': faqs})

# About page view
def about(request):
    return render(request, 'tickets/about.html')

# Contact page view
def contact(request):
    return render(request, 'tickets/contact.html')

# User registration view
def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Log the user in after registration
            login(request, user)
            messages.success(request, 'Registration successful! Please complete your profile.')
            return redirect('profile')
    else:
        form = CustomerRegistrationForm()
    return render(request, 'tickets/register.html', {'form': form})

# User profile view
@login_required(login_url='login')
def profile(request):
    try:
        user_meta = UserMeta.objects.get(user=request.user)
    except UserMeta.DoesNotExist:
        # Create user meta if it doesn't exist
        user_role, _ = Role.objects.get_or_create(name='user')
        user_meta = UserMeta.objects.create(user=request.user, role=user_role)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=user_meta)
        if form.is_valid():
            profile = form.save(commit=False)
            # Update user's first and last name
            request.user.first_name = form.cleaned_data['first_name']
            request.user.last_name = form.cleaned_data['last_name']
            request.user.save()
            
            # Mark profile as completed
            profile.is_profile_completed = True
            profile.save()
            
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('dashboard')
    else:
        form = UserProfileForm(instance=user_meta)
    
    return render(request, 'tickets/profile.html', {'form': form})

# User dashboard view
@login_required(login_url='login')
def dashboard(request):
    user = request.user
    role = user.user_meta.role.name.lower()
    
    # Get ticket statistics based on user role
    if role == 'admin':
        # For admin, show all tickets and stats
        stats = {
            'total': Ticket.objects.count(),
            'pending': Ticket.objects.filter(status='pending').count(),
            'in_progress': Ticket.objects.filter(status='in_progress').count(),
            'resolved': Ticket.objects.filter(status='resolved').count(),
            'closed': Ticket.objects.filter(status='closed').count(),
        }
        tickets = Ticket.objects.all().order_by('-created_at')[:10]  # Recent 10 tickets for admin
        
    elif role == 'support_agent':
        # For support agents, show only assigned tickets
        assigned_tickets = Ticket.objects.filter(assigned_to=user)
        stats = {
            'total': assigned_tickets.count(),
            'pending': assigned_tickets.filter(status='pending').count(),
            'in_progress': assigned_tickets.filter(status='in_progress').count(),
            'resolved': assigned_tickets.filter(status='resolved').count(),
            'closed': assigned_tickets.filter(status='closed').count(),
        }
        tickets = assigned_tickets.order_by('-created_at')[:10]  # Recent 10 assigned tickets
        
    else:  # User
        # For users, show only their own tickets
        user_tickets = Ticket.objects.filter(user=user)
        stats = {
            'total': user_tickets.count(),
            'pending': user_tickets.filter(status='pending').count(),
            'in_progress': user_tickets.filter(status='in_progress').count(),
            'resolved': user_tickets.filter(status='resolved').count(),
            'closed': user_tickets.filter(status='closed').count(),
        }
        tickets = user_tickets.order_by('-created_at')  # All user tickets, newest first
        
    # Prepare context for the template
    context = {
        'user': user,
        'role': role,
        'tickets': tickets,
        'total_count': stats['total'],
        'pending_count': stats['pending'],
        'in_progress_count': stats['in_progress'],
        'resolved_count': stats['resolved'],
        'closed_count': stats.get('closed', 0),  # Use get to handle if closed isn't in stats
    }
    
    # Add website_contents to context if user is admin
    if role == 'admin':
        return render(request, 'tickets/dashboard_admin.html', context)
    elif role == 'support_agent':
        return render(request, 'tickets/dashboard_support.html', context)
    else:  # User
        return render(request, 'tickets/dashboard.html', context)

@login_required(login_url='login')
def ticket_list(request):
    """View for listing tickets with filtering and search capabilities"""
    user = request.user
    role = user.user_meta.role.name
    
    # Base queryset depends on user role
    if role == 'admin':
        tickets = Ticket.objects.all()
    elif role == 'support':
        tickets = Ticket.objects.filter(assigned_to=user)
    else:  # User
        tickets = Ticket.objects.filter(user=user)
    
    # Get all categories for the filter dropdown
    categories = TicketCategory.objects.all()
    
    # Handle filters
    status = request.GET.get('status', '')
    priority = request.GET.get('priority', '')
    category = request.GET.get('category', '')
    search_query = request.GET.get('q', '')
    
    # Apply filters
    if status:
        tickets = tickets.filter(status=status)
    
    if priority:
        tickets = tickets.filter(priority=priority)
    
    if category:
        tickets = tickets.filter(category_id=category)
    
    if search_query:
        tickets = tickets.filter(
            Q(title__icontains=search_query) | 
            Q(description__icontains=search_query) |
            Q(id__icontains=search_query)
        )
    
    # Order by most recent
    tickets = tickets.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(tickets, 10)  # Show 10 tickets per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'tickets': page_obj,
        'categories': categories,
        'status': status,
        'priority': priority,
        'category': category,
        'search_query': search_query,
        'role': role
    }
    
    return render(request, 'tickets/ticket_list.html', context)

# Create ticket view
@login_required(login_url='login')
def create_ticket(request):
    if not hasattr(request.user, 'user_meta') or not request.user.user_meta.is_profile_completed:
        messages.warning(request, 'Please complete your profile first.')
        return redirect('profile')
        
    if request.method == 'POST':
        ticket_form = TicketForm(request.POST)
        
        if ticket_form.is_valid():
            # Save the ticket
            ticket = ticket_form.save(commit=False)
            ticket.user = request.user
            ticket.save()
            
            # Save multiple attachments if provided
            files = request.FILES.getlist('attachments')
            allowed_extensions = ['jpg', 'jpeg', 'png', 'gif', 'pdf', 'doc', 'docx', 'xls', 'xlsx', 'txt']
            
            for file in files:
                # Get file extension
                filename = file.name
                extension = filename.split('.')[-1].lower()
                
                # Validate file type
                if extension in allowed_extensions:
                    # Create the media object with file type info
                    Media.objects.create(
                        file=file,
                        ticket=ticket,
                        user=request.user,
                        file_type=extension
                    )
                else:
                    messages.warning(request, f'File {filename} was not uploaded. Only {", ".join(allowed_extensions)} files are allowed.')
                
            # Create a ticket action to log ticket creation
            TicketAction.objects.create(
                ticket=ticket,
                performed_by=request.user,
                action_type='note',
                notes='Ticket created by user'
            )
                
            messages.success(request, 'Your ticket has been created successfully!')
            return redirect('ticket_detail', ticket_id=ticket.id)
    else:
        ticket_form = TicketForm()
    
    categories = TicketCategory.objects.all()
    return render(request, 'tickets/create_ticket.html', {
        'ticket_form': ticket_form,
        'categories': categories
    })

# Ticket detail view
@login_required(login_url='login')
def ticket_detail(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    
    # Check permission to view this ticket based on role
    role = request.user.user_meta.role.name.lower()
    
    # Users can only view their own tickets
    if role == 'user' and ticket.user != request.user:
        messages.error(request, "You don't have permission to view this ticket.")
        return redirect('ticket_list')
    
    # Support agents can only view tickets assigned to them
    if role == 'support_agent' and ticket.assigned_to != request.user:
        messages.error(request, "You can only view tickets assigned to you.")
        return redirect('ticket_list')
    
    # Process form submissions
    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        
        # Process response form
        if form_type == 'response':
            response_form = TicketResponseForm(request.POST)
            if response_form.is_valid():
                response = response_form.save(commit=False)
                response.ticket = ticket
                response.user = request.user
                response.save()
                
                # Handle file uploads for the response
                files = request.FILES.getlist('attachments')
                for file in files:
                    Media.objects.create(
                        file=file,
                        ticket=ticket,
                        user=request.user
                    )
                
                # Log this action if not made by the user
                if role != 'user':
                    TicketAction.objects.create(
                        ticket=ticket,
                        performed_by=request.user,
                        action_type='response',
                        notes=f"Added response: {response.message[:50]}{'...' if len(response.message) > 50 else ''}"
                    )
                
                # Update ticket status if it was pending and a support agent responded
                if ticket.status == 'pending' and role in ['admin', 'support_agent']:
                    ticket.status = 'in_progress'
                    ticket.save()
                    messages.info(request, 'Ticket status automatically updated to In Progress.')
                
                messages.success(request, 'Your response has been added successfully.')
                return redirect('ticket_detail', ticket_id=ticket.id)
        
        # Process action form (admin/support only)
        elif form_type == 'action' and role in ['admin', 'support_agent']:
            action_form = TicketActionForm(request.POST)
            if action_form.is_valid():
                # Create the action record
                action = action_form.save(commit=False)
                action.ticket = ticket
                action.performed_by = request.user
                
                # Update ticket status if action involves status change
                action_type = action.action_type
                if action_type in ['resolve', 'close']:
                    ticket.status = 'resolved' if action_type == 'resolve' else 'closed'
                    ticket.save()
                    messages.success(request, f'Ticket status updated to {ticket.get_status_display()}')
                    
                # Log the action
                action.save()
                
                # Notify the user about the action
                messages.success(request, 'Action logged successfully!')
                return redirect('ticket_detail', ticket_id=ticket.id)
    
    # Initialize forms
    response_form = TicketResponseForm()
    action_form = TicketActionForm()
    
    # Gather ticket information
    responses = ticket.responses.all().order_by('created_at')
    actions = ticket.actions.all().order_by('-created_at')
    ticket_files = Media.objects.filter(ticket=ticket)
    
    # Create activity timeline (combine responses and actions, sorted by time)
    timeline_items = []
    for response in responses:
        timeline_items.append({
            'type': 'response',
            'user': response.user,
            'content': response.message,
            'time': response.created_at,
            'files': Media.objects.filter(ticket=ticket, user=response.user),
            'id': response.id
        })
    
    for action in actions:
        if action.action_type != 'note' or role in ['admin', 'support_agent']:  # Show notes only to staff
            timeline_items.append({
                'type': 'action',
                'user': action.performed_by,
                'content': action.notes,
                'action_type': action.get_action_type_display(),
                'action_taken': action.action_taken,
                'resolution_summary': action.resolution_summary,
                'time': action.created_at,
                'id': action.id
            })
    
    # Sort timeline by time (ascending)
    timeline_items.sort(key=lambda x: x['time'])
    
    context = {
        'ticket': ticket,
        'responses': responses,
        'response_form': response_form,
        'action_form': action_form,
        'timeline': timeline_items,
        'role': role,
        'ticket_files': ticket_files
    }
    
    return render(request, 'tickets/ticket_detail.html', context)

# Update ticket status view (for admin and support)
@login_required(login_url='login')
def update_ticket_status(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    
    # Check if user has permission to update the ticket
    user_meta = request.user.user_meta
    role = user_meta.role.name if user_meta.role else 'user'
    
    if role not in ['support', 'admin'] or (role == 'support' and ticket.assigned_to != request.user):
        return HttpResponseForbidden("You don't have permission to update this ticket.")
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in [status[0] for status in Ticket.STATUS_CHOICES]:
            ticket.status = new_status
            ticket.save()
            messages.success(request, f'Ticket status updated to {dict(Ticket.STATUS_CHOICES)[new_status]}.')
        
        # If the ticket is being assigned
        if 'assigned_to' in request.POST and role == 'admin':
            agent_id = request.POST.get('assigned_to')
            if agent_id:
                from django.contrib.auth.models import User
                try:
                    agent = User.objects.get(id=agent_id)
                    # Check if agent has support role
                    if hasattr(agent, 'user_meta') and agent.user_meta.role and agent.user_meta.role.name == 'support':
                        ticket.assigned_to = agent
                        ticket.save()
                        messages.success(request, f'Ticket assigned to {agent.username}.')
                except User.DoesNotExist:
                    messages.error(request, 'Selected support agent does not exist.')
    
    return redirect('ticket_detail', ticket_id=ticket.id)

# FAQ view
def faq(request):
    # Get search parameters
    query = request.GET.get('q', None)
    category = request.GET.get('category', None)
    
    # Base queryset - only show published FAQs
    faqs = FAQKnowledgeBase.objects.filter(is_published=True)
    
    # Apply search if query provided
    if query:
        faqs = faqs.filter(Q(question__icontains=query) | Q(answer__icontains=query))
    
    # Apply category filter if provided
    if category and category != 'all':
        faqs = faqs.filter(category=category)
    
    # Get distinct categories for the filter - use set to ensure uniqueness
    category_values = set(FAQKnowledgeBase.objects.filter(is_published=True).values_list('category', flat=True))
    category_choices = dict(FAQKnowledgeBase.CATEGORY_CHOICES)
    
    # Only display categories that have FAQs
    available_categories = []
    for cat in category_values:
        available_categories.append((cat, category_choices.get(cat, cat)))
    
    # Sort categories by their display name for consistent ordering
    available_categories.sort(key=lambda x: x[1])
    
    context = {
        'faqs': faqs,
        'categories': available_categories,
        'current_category': category,
        'search_query': query
    }
    
    return render(request, 'tickets/faq.html', context)

# Admin FAQ management view
@login_required(login_url='login')
def manage_faq(request):
    user_meta = request.user.user_meta
    role = user_meta.role.name if user_meta.role else 'user'
    
    if role not in ['admin', 'support']:
        return HttpResponseForbidden("You don't have permission to manage FAQs.")
    
    faqs = FAQKnowledgeBase.objects.all().order_by('-created_at')
    
    if request.method == 'POST':
        form = FAQForm(request.POST)
        if form.is_valid():
            faq = form.save(commit=False)
            faq.created_by = request.user
            faq.save()
            messages.success(request, 'FAQ has been created successfully.')
            return redirect('manage_faq')
    else:
        form = FAQForm()
    
    return render(request, 'tickets/manage_faq.html', {'faqs': faqs, 'form': form})

# Custom login view for role-based redirection
def login_view(request):
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            
            # Redirect based on user role
            try:
                role = user.user_meta.role.name.lower()
                if role in ['admin', 'support_agent']:
                    # Admins and support agents go directly to admin panel
                    messages.success(request, f'Welcome back, {user.username}!')
                    return redirect('/admin/')
                else:
                    # Users go to dashboard
                    messages.success(request, f'Welcome back, {user.username}!')
                    return redirect('dashboard')
            except:
                # Default to dashboard if role check fails
                messages.success(request, f'Welcome back, {user.username}!')
                return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = CustomLoginForm(request)
    return render(request, 'tickets/login.html', {'form': form})

# Helper function to redirect users based on their role
def redirect_based_on_role(request):
    try:
        role = request.user.user_meta.role.name.lower()
        
        # Redirect support agents and admins to admin interface
        if role in ['support_agent', 'admin']:
            messages.info(request, f'{role.capitalize()} users should use the admin interface.')
            return redirect('/admin/')
        
        # Redirect users to dashboard
        elif role == 'user':
            return redirect('dashboard')
        
        # Default fallback
        else:
            return redirect('home')
    except Exception as e:
        # If role lookup fails, default to dashboard
        return redirect('home')
