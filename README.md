# 🗂️ TaskFlow — Smart Task & Workflow Management System  

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)  
[![Django](https://img.shields.io/badge/django-5.x-green.svg)](https://www.djangoproject.com/)  
[![Channels](https://img.shields.io/badge/django--channels-4.x-orange)](https://channels.readthedocs.io/)  
[![PostgreSQL - used Supabase](https://img.shields.io/badge/database-PostgreSQL-blue.svg)](https://www.postgresql.org/)  
[![Redis](https://img.shields.io/badge/cache-Redis-red.svg)](https://redis.io/)  
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)  

TaskFlow is a powerful **task and workflow management platform** built with Django and Django Channels.  
It is designed to help organizations streamline task assignment, manage dependencies, and enhance team collaboration through integrated real-time chat.  

---

## 🚀 Features  

### 👥 User & Company Management  
- **Company Creation**: New users can create and manage their company profile.  
- **Employee Management**: Managers add employees under their company.  
- **Email Invitations**:  
  - Employees receive login invitations via email.  
  - Employees get notified via email when assigned tasks.  

### ✅ Task Management  
- **Task Assignment**: Assign tasks to one or multiple employees.  
- **Task Dependencies**: Supports industry-standard dependencies:  
  - Start-to-Finish (SF)  
  - Finish-to-Finish (FF)  
  - Start-to-Start (SS)  
  - Finish-to-Start (FS)  
- **Task Status**: Automatically updates (`Pending`, `Suspended`, etc.) based on dependencies.  
- **Timeline Management**: Start & end dates dynamically adjust according to dependencies.  

### 💬 Real-Time Collaboration  
- **Task Chat Rooms**:  
  - When multiple employees are assigned, a chat group is created.  
  - Powered by **Django Channels** for WebSocket-based messaging.  
- **Manager Oversight**: Managers have access to all chat rooms.  

### 🔁 Workflow Templates  
- **Reusable Templates**: Define sequences of repeatable tasks.  
- **Task Prototypes**: Templates contain task “models.”  
- **Template Deployment**: Deploying generates actual tasks linked to a workflow instance.  
- **Reusability**: Templates can be used multiple times across projects.  

---

## 🛠️ Tech Stack  

- **Backend**: Django, Django MVT
- **Real-Time Communication**: Django Channels (WebSockets)  
- **Database**: PostgreSQL  
- **Cache & Async**: Redis  
- **Frontend**: Django Templates 
- **Auth & Emails**: Django Auth + SMTP  

---

## 📂 Project Structure  

```bash
taskflow/
│── company/           # Company & employee management  
│── leadss/             # Core task management and dependencies  
│── automation/         # Workflow templates and instances  
│── chat/              # Real-time chat (Django Channels)  
│── employees/          # Employee management  
│── templates/         # Frontend templates  
│── static/            # Static files  
│── manage.py  

