# TMS Application

This folder contains the Django TMS (Ticket Management System) application source code.

## 📁 Application Structure

```
app/
├── 📁 tms/                  # Django project settings
│   ├── __init__.py          # Python package marker
│   ├── settings.py          # Development settings
│   ├── settings_production.py # Production settings
│   ├── urls.py              # Main URL configuration
│   ├── wsgi.py              # WSGI application entry point
│   └── asgi.py              # ASGI application entry point
├── 📁 tickets/              # Tickets application
│   ├── __init__.py          # Python package marker
│   ├── admin.py             # Django admin configuration
│   ├── apps.py              # Application configuration
│   ├── forms.py             # Form definitions
│   ├── models.py            # Database models
│   ├── views.py             # View functions and classes
│   ├── urls.py              # URL routing for tickets
│   ├── signals.py           # Django signals
│   ├── middleware.py        # Custom middleware
│   ├── templatetags/        # Custom template tags
│   └── management/          # Management commands
├── 📁 templates/            # HTML templates
│   ├── base.html            # Base template
│   ├── admin/               # Admin interface templates
│   └── tickets/             # Ticket-specific templates
├── 📁 static/               # Static files
│   ├── css/                 # Stylesheets
│   ├── js/                  # JavaScript files
│   └── img/                 # Images and icons
├── 📁 media/                # User uploaded files
├── manage.py                # Django management script
├── requirements.txt          # Python dependencies
├── Dockerfile               # Production Docker image
├── DockerfileDev            # Development Docker image
└── env.example              # Environment variables template
```

## 🚀 Quick Start

### 1. Setup Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### 2. Install Dependencies
```bash
# Install Python packages
pip install -r requirements.txt
```

### 3. Environment Configuration
```bash
# Copy environment template
cp env.example .env

# Edit .env with your settings
# Required variables:
# - SECRET_KEY
# - DEBUG
# - DATABASE_URL or individual DB settings
```

### 4. Database Setup
```bash
# Run database migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Load sample data (optional)
python manage.py loaddata sample_data
```

### 5. Run Development Server
```bash
# Start development server
python manage.py runserver

# Access application at: http://localhost:8000
# Access admin at: http://localhost:8000/admin
```

## 🏗️ Architecture

### Django Components
- **Models**: Database schema and business logic
- **Views**: Request handling and response generation
- **Forms**: Data validation and user input handling
- **Templates**: HTML presentation layer
- **Admin**: Built-in administration interface

### Key Features
- **User Management**: Authentication and authorization
- **Role-Based Access**: Customer, Support, Admin roles
- **Ticket System**: Create, track, and manage tickets
- **FAQ System**: Knowledge base management
- **File Uploads**: Document and image handling
- **Email Notifications**: Automated communication

## 🔧 Development

### Code Style
- Follow PEP 8 Python style guide
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions small and focused

### Testing
```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test tickets

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

### Database Operations
```bash
# Create new migration
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Show migration status
python manage.py showmigrations

# Reset database (development only)
python manage.py flush
```

### Static Files
```bash
# Collect static files
python manage.py collectstatic

# Clear static files cache
python manage.py collectstatic --clear
```

## 🐳 Docker Development

### Build Development Image
```bash
# Build development image
docker build -f DockerfileDev -t tms-dev .

# Run development container
docker run -d \
  -v $(pwd):/app \
  -p 8054:8000 \
  --rm --name tms-dev-container \
  tms-dev
```

### Build Production Image
```bash
# Build production image
docker build -f Dockerfile -t tms-prod .

# Run production container
docker run -d \
  -p 8000:8000 \
  --env-file .env \
  --name tms-prod-container \
  tms-prod
```

## 📊 Database Models

### Core Models
- **User**: Extended user model with roles
- **Ticket**: Main ticket entity
- **TicketAction**: Ticket lifecycle actions
- **FAQKnowledgeBase**: Knowledge base articles
- **FAQCategory**: FAQ organization

### Relationships
- Users can have multiple tickets
- Tickets have multiple actions
- FAQs are organized by categories
- Actions track ticket changes

## 🔒 Security Features

### Authentication
- Django's built-in authentication system
- Password validation and hashing
- Session management

### Authorization
- Role-based access control
- Permission-based views
- Middleware for access control

### Data Protection
- CSRF protection
- XSS prevention
- SQL injection protection
- File upload validation

## 📱 Frontend

### Templates
- **Base Template**: Common layout and navigation
- **Admin Templates**: Custom admin interface
- **Ticket Templates**: Ticket management interface
- **User Templates**: User dashboard and forms

### Static Assets
- **CSS**: Custom styling and Jazzmin theme
- **JavaScript**: Interactive functionality
- **Images**: Icons and graphics

### Responsive Design
- Mobile-friendly interface
- Bootstrap-based layout
- Progressive enhancement

## 🚀 Production Deployment

### Environment Variables
```bash
# Required for production
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=your-domain.com
DATABASE_URL=mysql://user:pass@host:port/db

# Optional security settings
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

### Performance Optimization
- **Static Files**: Served by web server
- **Database**: Connection pooling
- **Caching**: Redis or Memcached
- **Compression**: Gzip compression

### Monitoring
- **Logging**: Structured logging
- **Health Checks**: Application health endpoints
- **Metrics**: Performance monitoring
- **Error Tracking**: Exception monitoring

## 🔍 Debugging

### Development Tools
- **Django Debug Toolbar**: Development debugging
- **Logging**: Application logging
- **Shell**: Interactive Python shell

### Common Issues
- **Database Connections**: Check connection settings
- **Static Files**: Verify collectstatic
- **Permissions**: Check file permissions
- **Environment**: Verify environment variables

## 📚 Additional Resources

- **[Django Documentation](https://docs.djangoproject.com/)** - Official Django docs
- **[Django REST Framework](https://www.django-rest-framework.org/)** - API development
- **[Jazzmin Documentation](https://django-jazzmin.readthedocs.io/)** - Admin theme
- **[MySQL Documentation](https://dev.mysql.com/doc/)** - Database reference

## 🤝 Contributing

### Development Workflow
1. Create feature branch
2. Make changes with tests
3. Run test suite
4. Update documentation
5. Submit pull request

### Code Review
- All changes require review
- Tests must pass
- Documentation must be updated
- Code style must be followed 