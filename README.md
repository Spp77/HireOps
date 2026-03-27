# HireOps

HireOps is a production-grade, highly scalable job portal, engineered to facilitate connections between job seekers and recruiters. Inspired by industry-leading platforms such as Indeed, this project is designed for robust performance, horizontal scaling, and enterprise-level system architecture.

## Architecture & System Design

The application follows a distributed architecture utilizing the following core components:

- **Web Application Server**: Built on Django and Django REST Framework, handling core business logic, API operations, and strict role-based access control.
- **Asynchronous Task Queue**: Utilizing Celery and supported by Redis to offload heavy background processes (e.g., email notifications, data processing), ensuring low-latency API response times.
- **Caching Layer**: Redis is employed for in-memory caching to optimize query performance and reduce recurrent database load.
- **Database System**: Engineered for PostgreSQL, with support for read-replica routing to scale database read operations independently of write operations.
- **Security Standards**: Hardened via OWASP-compliant security headers, strict environment segregation (Base, Development, Production configurations), and secure session management.

## Technology Stack

- **Backend Framework**: Python 3.10+, Django, Django REST Framework
- **Primary Database**: PostgreSQL
- **Message Broker & Cache**: Redis
- **Task Worker**: Celery
- **Containerization**: Docker & Docker Compose
- **Dependency Management**: Pipenv

## Core Project Structure

```text
HireOps/
├── apps/               # Isolated application modules (companies, jobs, users)
├── config/             # Environment-specific configuration configurations (base, dev, prod)
├── docker-compose.yml  # Multi-container orchestration definition
├── Dockerfile          # Web container image build instructions
└── Pipfile             # Deterministic dependency specifications
```

## Provisioning and Setup

The application deployment workflow utilizes Docker Compose to ensure strict environment parity across development, staging, and production deployments.

### Prerequisites

Ensure the host machine or deployment environment has the following dependencies provisioned:
- Docker Engine (v20.10.0 or higher)
- Docker Compose (v2.0.0 or higher)

### Environment Initialization

1. Clone the repository to your host environment:
   ```bash
   git clone https://github.com/Spp77/HireOps.git
   cd HireOps
   ```

2. Establish the environment configuration:
   ```bash
   cp .env.example .env
   ```
   *Note: Modify the `.env` file with appropriate production secrets, database credentials, and API keys prior to deployment.*

3. Provision the infrastructure and execute the container build pipeline:
   ```bash
   docker-compose up --build -d
   ```

4. Execute database migrations to construct the requisite schema:
   ```bash
   docker-compose exec web python manage.py migrate
   ```

5. The service will begin listening on port `8000`. Navigate to `http://localhost:8000` or the mapped external IP address.

## Authorization & Access Control

Role-based access is strictly enforced across all REST endpoints. The system authenticates two primary entities:
- **Recruiters**: Possess complete CRUD authorization over job postings, applicant tracking, and company profiles.
- **Candidates**: Maintain read/write control over their personal profiles, resumes, saved job states, and application histories.
