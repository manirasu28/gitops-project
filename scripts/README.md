# Utility Scripts

This folder contains utility scripts for managing the TMS application, including database setup, user management, and data maintenance.

## 📁 Scripts Overview

```
scripts/
├── create_superuser.py       # Create Django superuser
├── create_roles.py           # Setup user roles and permissions
├── add_user_role.py          # Assign roles to existing users
├── add_faq_categories.py     # Create FAQ categories
├── check_faq_data.py         # Verify FAQ data integrity
├── fix_action_table.py       # Fix ticket action table issues
├── fix_actions.py            # Fix ticket action data
├── fix_database.py           # General database fixes
├── create_sample_data.py     # Generate sample data for testing
└── README.md                 # This file
```

## 🚀 Quick Usage

### 1. Setup Initial Data
```bash
cd app
python ../scripts/create_roles.py
python ../scripts/create_superuser.py
python ../scripts/add_faq_categories.py
```

### 2. Create Sample Data
```bash
cd app
python ../scripts/create_sample_data.py
```

### 3. Fix Database Issues
```bash
cd app
python ../scripts/fix_database.py
```

## 📋 Script Details

### User Management Scripts

#### `create_superuser.py`
Creates a Django superuser account for administrative access.

**Usage:**
```bash
cd app
python ../scripts/create_superuser.py
```

**Features:**
- Interactive username and email input
- Secure password creation
- Validation of input data
- Error handling for duplicate users

#### `create_roles.py`
Sets up the initial user roles and permissions system.

**Usage:**
```bash
cd app
python ../scripts/create_roles.py
```

**Creates:**
- Customer role
- Support role
- Admin role
- Associated permissions

#### `add_user_role.py`
Assigns roles to existing users in the system.

**Usage:**
```bash
cd app
python ../scripts/add_user_role.py
```

**Features:**
- List existing users
- Select user and role
- Update user profile
- Validation of role assignments

### Data Management Scripts

#### `add_faq_categories.py`
Creates initial FAQ categories for organizing knowledge base articles.

**Usage:**
```bash
cd app
python ../scripts/add_faq_categories.py
```

**Creates Categories:**
- General Information
- Technical Support
- Billing & Payments
- Account Management
- Troubleshooting

#### `create_sample_data.py`
Generates sample data for testing and demonstration purposes.

**Usage:**
```bash
cd app
python ../scripts/create_sample_data.py
```

**Generates:**
- Sample users with different roles
- Sample tickets with various statuses
- Sample FAQ articles
- Sample ticket actions

### Database Maintenance Scripts

#### `check_faq_data.py`
Verifies the integrity of FAQ data and reports any issues.

**Usage:**
```bash
cd app
python ../scripts/check_faq_data.py
```

**Checks:**
- FAQ category existence
- Article associations
- Data consistency
- Missing relationships

#### `fix_action_table.py`
Fixes issues in the ticket action table structure and data.

**Usage:**
```bash
cd app
python ../scripts/fix_action_table.py
```

**Fixes:**
- Missing action records
- Inconsistent action data
- Orphaned action entries
- Action sequence issues

#### `fix_actions.py`
Repairs ticket action data and relationships.

**Usage:**
```bash
cd app
python ../scripts/fix_actions.py
```

**Repairs:**
- Action timestamps
- User associations
- Action descriptions
- Status transitions

#### `fix_database.py`
General database maintenance and repair operations.

**Usage:**
```bash
cd app
python ../scripts/fix_database.py
```

**Operations:**
- Database connection testing
- Table structure verification
- Data integrity checks
- Common issue resolution

## 🔧 Script Requirements

### Prerequisites
- Django application must be properly configured
- Database must be accessible
- Required models must be migrated
- Environment variables must be set

### Environment Setup
```bash
# Ensure you're in the app directory
cd app

# Set Django environment
export DJANGO_SETTINGS_MODULE=tms.settings

# Or use production settings
export DJANGO_SETTINGS_MODULE=tms.settings_production
```

### Database Access
Scripts require database access with appropriate permissions:
- Read access to user tables
- Write access to role and permission tables
- Access to FAQ and ticket tables

## 🚨 Error Handling

### Common Issues

#### 1. Import Errors
```python
# Error: No module named 'django'
# Solution: Ensure you're in the app directory and Django is installed
cd app
pip install -r requirements.txt
```

#### 2. Database Connection Errors
```python
# Error: Database connection failed
# Solution: Check database settings and connectivity
python manage.py dbshell
```

#### 3. Permission Errors
```python
# Error: Permission denied
# Solution: Ensure database user has appropriate permissions
```

### Debug Mode
Most scripts include debug output:
```bash
# Enable verbose output
export DEBUG=True
python ../scripts/script_name.py
```

## 📊 Script Output

### Success Indicators
- **User Creation**: "User created successfully"
- **Role Assignment**: "Role assigned successfully"
- **Data Creation**: "Data created successfully"
- **Database Fixes**: "Database issues resolved"

### Error Reporting
- **Validation Errors**: Input validation failures
- **Database Errors**: Connection or query issues
- **Permission Errors**: Access control violations
- **Data Errors**: Integrity or consistency issues

## 🔒 Security Considerations

### User Creation
- Passwords are securely hashed
- Email validation is performed
- Duplicate user prevention
- Role-based access control

### Data Validation
- Input sanitization
- SQL injection prevention
- XSS protection
- Data integrity checks

### Access Control
- Script execution permissions
- Database access controls
- User role validation
- Audit trail maintenance

## 📚 Best Practices

### Script Development
- Use descriptive function names
- Include error handling
- Add logging and debugging
- Validate all inputs
- Handle edge cases

### Execution
- Run scripts in order of dependency
- Backup database before major changes
- Test in development environment
- Monitor script execution
- Document any manual steps

### Maintenance
- Regular script updates
- Version control for scripts
- Change documentation
- Testing after updates
- Rollback procedures

## 🆘 Troubleshooting

### Script Failures
1. **Check Environment**: Ensure Django is properly configured
2. **Verify Database**: Test database connectivity
3. **Check Permissions**: Ensure adequate database access
4. **Review Logs**: Check Django and script output
5. **Validate Data**: Verify input data integrity

### Common Solutions
```bash
# Reset Django environment
unset DJANGO_SETTINGS_MODULE
cd app
export DJANGO_SETTINGS_MODULE=tms.settings

# Test database connection
python manage.py dbshell

# Check Django configuration
python manage.py check
```

## 📞 Support

For script-related issues:
1. Check script output and error messages
2. Verify Django configuration
3. Test database connectivity
4. Review script documentation
5. Consult Django documentation

## 🎯 Future Enhancements

### Planned Features
- **Automated Testing**: Unit tests for all scripts
- **Configuration Files**: External configuration support
- **Logging**: Comprehensive logging system
- **Rollback**: Automatic rollback capabilities
- **Monitoring**: Script execution monitoring

### Script Improvements
- **Error Recovery**: Automatic error recovery
- **Progress Tracking**: Execution progress indicators
- **Validation**: Enhanced input validation
- **Documentation**: Inline help and examples
- **Integration**: CI/CD pipeline integration 