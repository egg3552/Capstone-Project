# Django Blog Platform

A production-ready blog platform built with Django 5.2.6, featuring user authentication, content management, and deployment on Heroku.

## 🚀 Live Demo
**[https://capstone-blog-matthew-eb1d04bfcf98.herokuapp.com/](https://capstone-blog-matthew-eb1d04bfcf98.herokuapp.com/)**

## Features
- User registration, login/logout with role-based access
- Create, edit, delete blog posts with categories and tags
- Comment system with moderation
- Search and filtering capabilities
- Mobile-responsive Bootstrap 5 design
- PostgreSQL database with Heroku deployment

## Tech Stack
- **Backend**: Django 5.2.6, PostgreSQL, Gunicorn
- **Frontend**: Bootstrap 5, HTML/CSS/JavaScript
- **Deployment**: Heroku with WhiteNoise for static files
- **Environment**: django-environ for configuration

## Quick Start

### Local Development
```bash
git clone https://github.com/egg3552/Capstone-Project.git
cd BlogFullStackProject

# Setup environment
python -m venv .venv
.\.venv\Scripts\activate  # Windows
pip install -r requirements.txt

# Configure database
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Environment Variables
Create `.env` file:
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
DATABASE_URL=sqlite:///db.sqlite3
```

## Project Structure
```
BlogFullStackProject/
├── blog/               # Main application
├── blogproject/        # Settings and configuration
├── templates/          # HTML templates
├── static/            # CSS, JS, images
└── requirements.txt   # Dependencies
```

## Deployment Notes
Successfully deployed on Heroku with:
- PostgreSQL database integration
- Environment-based configuration
- Static file handling with WhiteNoise
- Resolved WSGI module case sensitivity issues

## Quality Assurance
- AI-assisted debugging and code review using GitHub Copilot
- Comprehensive testing for security vulnerabilities and best practices
- Manual testing of all user flows and functionality

---
Built with Django 5.2.6 | Deployed on Heroku | AI-Assisted Development