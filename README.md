# 🚀 Task Flow

A comprehensive enterprise-level task management platform built with Django, featuring real-time collaboration, workflow automation, and intelligent task dependencies.

## ✨ Key Features

### 🏢 **Multi-Tenant Company Management**
- **Company Creation**: New users can create and manage their own company workspace
- **Employee Management**: Add, invite, and manage employees within your organization
- **Role-Based Access Control**: Hierarchical permissions with managers having full oversight

### 📧 **Smart Email Integration**
- **Automated Invitations**: New employees receive welcome emails with login credentials
- **Task Notifications**: Real-time email alerts when tasks are assigned or updated
- **Status Updates**: Automated notifications for task progress and deadline reminders

### 📋 **Advanced Task Management**
- **Task Assignment**: Assign tasks to single or multiple employees
- **Dependency Management**: Support for various dependency types:
  - **Start-to-Finish**: Task B starts when Task A finishes
  - **Finish-to-Finish**: Task B finishes when Task A finishes
  - **Start-to-Start**: Task B starts when Task A starts
  - **Finish-to-Start**: Task B starts when Task A finishes
- **Dynamic Status Tracking**: Automatic status updates (Pending, In Progress, Suspended, Completed) based on dependencies
- **Smart Date Calculation**: Automatic start/end date adjustment based on task relationships

### 💬 **Real-Time Collaboration**
- **Task-Specific Chat Rooms**: Dedicated chat groups for multi-employee tasks
- **Manager Oversight**: Company managers have access to all communication channels
- **Real-Time Messaging**: Powered by Django Channels for instant communication
- **WebSocket Integration**: Live updates without page refreshes

### 🔄 **Workflow Templates & Automation**
- **Template Creation**: Build reusable workflow templates for recurring processes
- **Task Prototypes**: Define task models that become actual tasks when deployed
- **Template Instances**: Track and manage multiple deployments of the same template
- **Batch Task Creation**: Deploy entire workflows with a single action
- **Template Reusability**: Use templates across multiple projects and time periods

### 👥 **User Experience & Security**
- **Employee-Centric Views**: Employees see only their assigned tasks
- **Intuitive Dashboard**: Clean, responsive interface for all user types
- **Secure Authentication**: Robust login system with email verification
- **Permission Management**: Fine-grained access control across all features

## 🛠 Technical Stack

- **Backend**: Django (Python)
- **Real-Time**: Django Channels (WebSockets)
- **Database**: PostgreSQL/MySQL (configurable)
- **Email**: Django Email Backend
- **Frontend**: HTML5, CSS3, JavaScript
- **Authentication**: Django Auth System

## 📦 Installation

### Prerequisites
- Python 3.8+
- PostgreSQL/MySQL
- Redis (for Django Channels)

### Quick Start

```bash
# Clone the repository
git clone https://github.com/yourusername/task-management-system.git
cd task-management-system

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your database and email settings

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start Redis server (for WebSockets)
redis-server

# Run the development server
python manage.py runserver
```

## 🚀 Usage

### For Company Managers

1. **Setup Your Company**
   ```
   → Register → Create Company → Add Company Details
   ```

2. **Invite Employees**
   ```
   → Employees → Add Employee → Send Invitation
   ```

3. **Create Workflow Templates**
   ```
   → Templates → New Template → Add Task Prototypes → Save
   ```

4. **Deploy Projects**
   ```
   → Projects → New Project → Select Template → Deploy
   ```

### For Employees

1. **Join Your Company**
   ```
   → Check Email → Click Invitation Link → Set Password
   ```

2. **Manage Your Tasks**
   ```
   → Dashboard → View Assigned Tasks → Update Status
   ```

3. **Collaborate**
   ```
   → Task Details → Join Chat Room → Communicate
   ```

## 🔧 Configuration

### Email Settings
```python
# settings.py
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'your-smtp-host.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@company.com'
EMAIL_HOST_PASSWORD = 'your-password'
```

### WebSocket Configuration
```python
# settings.py
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],
        },
    },
}
```

## 📊 Task Dependencies

The system supports four types of task dependencies:

| Dependency Type | Description | Use Case |
|----------------|-------------|----------|
| **Finish-to-Start (FS)** | Task B starts when Task A finishes | Sequential tasks |
| **Start-to-Start (SS)** | Task B starts when Task A starts | Parallel tasks with synchronized start |
| **Finish-to-Finish (FF)** | Task B finishes when Task A finishes | Tasks with synchronized completion |
| **Start-to-Finish (SF)** | Task B finishes when Task A starts | Just-in-time scenarios |

## 🎯 API Endpoints

```
POST   /api/companies/          # Create company
GET    /api/employees/          # List employees
POST   /api/employees/          # Add employee
POST   /api/tasks/              # Create task
GET    /api/tasks/assigned/     # Get assigned tasks
POST   /api/templates/          # Create template
POST   /api/templates/deploy/   # Deploy template
GET    /api/chat/rooms/         # List chat rooms
```

### Manual Deployment

```bash
# Install production dependencies
pip install -r requirements-prod.txt

# Collect static files
python manage.py collectstatic --noinput

# Run with Gunicorn
gunicorn project.wsgi:application --bind 0.0.0.0:8000
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- 📧 Email: support@taskmanagement.com
- 📚 Documentation: [Wiki](https://github.com/yourusername/task-management-system/wiki)
- 🐛 Bug Reports: [Issues](https://github.com/yourusername/task-management-system/issues)

## 🙏 Acknowledgments

- Django Team for the excellent framework
- Django Channels for WebSocket support
- Contributors and beta testers

---

**Built with ❤️ for modern teams who value efficiency and collaboration.**