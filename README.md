# HireOps

**HireOps** is a production-grade, highly scalable job portal inspired by Indeed. It connects job seekers with recruiters through a robust platform built with Django. The application is designed to be highly reliable, horizontally and vertically scalable, and deeply customizable.

---

## 🚀 Features

- **Robust Authentication & Authorization**: Secure accounts for both Job Seekers and Recruiters with role-based access control.
- **Candidate Profiles**: Comprehensive profiles for candidates to showcase their skills and resumes.
- **Job Management**: Complete CRUD operations for recruiters to post and manage job listings.
- **Advanced Filtering & Search**: Powerful search capability powered by `django-filter` to find jobs rapidly.
- **Job Applications & Saving**: Apply to jobs seamlessly or save them for later.
- **Background Task Processing**: Uses **Celery** to handle email notifications and asynchronous tasks reliably.
- **Caching**: Leverages **Redis** to cache frequently queried data and speed up the application.
- **Security Hardening**: Secure, OWASP-compliant headers, database read-replica routing support, and environment-specific settings configurations (base, dev, prod).
- **Containerized Ecosystem**: Fully Dockerized with `docker-compose` for an effortless local development and deployment experience.

---

## 🛠 Tech Stack

- **Backend Framework**: [Django](https://www.djangoproject.com/) & [Django REST Framework](https://www.django-rest-framework.org/)
- **Database**: PostgreSQL (with Read-Replica Support)
- **Caching & Message Broker**: [Redis](https://redis.io/)
- **Asynchronous Tasks**: [Celery](https://docs.celeryq.dev/)
- **Containerization**: [Docker](https://www.docker.com/) & Docker Compose
- **Dependency Management**: Pipenv

---

## ⚙️ Local Development Setup

We use Docker to make local development exactly mimic our production environment without any hassle.

### Prerequisites
Make sure you have [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/) installed on your machine.

### Getting Started

1. **Clone the repository** (if you haven't already):
   ```bash
   git clone https://github.com/your-username/HireOps.git
   cd HireOps
   ```

2. **Configure Environment Variables**:
   Copy the example environment file and customize it as needed.
   ```bash
   cp .env.example .env
   ```

3. **Build and Run the Containers**:
   Fire up the Django application, Redis, Celery worker, and PostgreSQL database.
   ```bash
   docker-compose up --build
   ```

4. **Apply Migrations**:
   Run the database migrations to set up your schema.
   ```bash
   docker-compose exec web python manage.py migrate
   ```

5. **Access the Application**:
   Navigate to `http://localhost:8000` in your web browser.

---

## 📂 Project Structure Overview

```text
HireOps/
├── apps/                 # Core Django apps (companies, jobs, users, etc.)
├── config/               # Django project-level settings (base, dev, prod)
├── docker-compose.yml    # Docker services configuration
├── Dockerfile            # Instructions to build the web container
├── Pipfile & Pipfile.lock# Dependency tracking
└── .env                  # Environment configurations
```

---

## 🚧 Contributing
As the project grows, ensure you test your changes locally and run all migrations before pushing any updates. Ensure that `.env` files are **never** committed to version control.

---

*This README is a living document and will be continuously updated as HireOps evolves.*
