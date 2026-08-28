# Budgeting App API

A RESTful budgeting API built with Django and Django REST Framework. The application allows authenticated users to create and manage budgets, categories, and transactions.

The project also supports recurring transactions using Celery and Celery Beat, with Redis acting as the message broker.

## Table of Contents

* [Features](#features)
* [Tech Stack](#tech-stack)
* [Project Architecture](#project-architecture)
* [Installation](#installation)
* [Environment Variables](#environment-variables)
* [Running the Application](#running-the-application)
* [Docker Setup](#docker-setup)
* [API Endpoints](#api-endpoints)

  * [Create Category](#create-category)
  * [Create Budget](#create-budget)
  * [Create Transaction](#create-transaction)
  * [Delete Category](#delete-category)
* [Recurring Transactions](#recurring-transactions)
* [Celery and Redis](#celery-and-redis)
* [Database Models](#database-models)
* [Future Improvements](#future-improvements)

---

## Features

* User authentication using JWT
* Create and manage monthly budgets
* One budget per user per month
* Create transaction categories
* Create income and expense transactions
* Automatically update the remaining budget balance
* Support for recurring transactions
* Weekly recurring transactions
* Monthly recurring transactions
* Yearly recurring transactions
* Background task processing with Celery
* Task scheduling with Celery Beat
* Redis as a Celery broker and result backend
* Docker support

---

## Tech Stack

* Python
* Django
* Django REST Framework
* SQLite
* Redis
* Celery
* Celery Beat
* django-celery-beat
* Docker

---

## Project Architecture

The application uses Django to handle API requests and Celery to process background tasks.

```text
Client
   |
   v
Django REST API
   |
   +-------------------+
   |                   |
   v                   v
Database              Redis
                        |
                +-------+-------+
                |               |
                v               v
          Celery Worker     Celery Beat
                |
                v
        Recurring Transactions
```

Celery Beat schedules recurring tasks, while the Celery worker processes them.

---

## Installation

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd Budgeting-App
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate the virtual environment.

Windows:

```bash
venv\Scripts\activate
```

Linux/macOS:

```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

---

## Environment Variables

Create a `.env` file in the root directory of the project.

Example:

```env
SECRET_KEY=your-secret-key
DEBUG=True
```

When running the application with Docker, the Redis hostname should use the Docker service name:

```env
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
```

When running Redis directly on your local machine without Docker:

```env
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

---

## Running the Application

Start the Django development server:

```bash
python manage.py runserver
```

The API will be available at:

```text
http://127.0.0.1:8000/
```

---

## Running Redis

If Redis is installed locally:

```bash
redis-server
```

Redis is used as the Celery message broker and result backend.

---

## Running Celery

Start the Celery worker:

```bash
celery -A project worker -l INFO
```

The worker processes background tasks sent by Celery Beat.

---

## Running Celery Beat

Start Celery Beat with the Django database scheduler:

```bash
celery -A project beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

Celery Beat is responsible for scheduling periodic tasks.

---

# Docker Setup

The project can also be run using Docker and Docker Compose.

The application consists of the following services:

* `web` - Django application
* `redis` - Redis message broker
* `celery` - Celery worker
* `celery-beat` - Celery Beat scheduler

Example Docker Compose structure:

```yaml
services:

  web:
    build: .
    command: python manage.py runserver 0.0.0.0:8000
    ports:
      - "8000:8000"
    env_file:
      - .env
    depends_on:
      - redis

  redis:
    image: redis:alpine
    ports:
      - "6379:6379"

  celery:
    build: .
    command: celery -A project worker -l INFO
    env_file:
      - .env
    depends_on:
      - redis

  celery-beat:
    build: .
    command: celery -A project beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler
    env_file:
      - .env
    depends_on:
      - redis
```

Build and start the containers:

```bash
docker compose up --build
```

To stop the containers:

```bash
docker compose down
```

---

# API Endpoints

All endpoints are prefixed with:

```text
/api/
```

## Create Category

Creates a new transaction category.

**Endpoint**

```http
POST /api/create-category/
```

Example request:

```json
{
    "name": "Food"
}
```

---

## Create Budget

Creates a budget for a user.

The application enforces the rule that a user can only have one budget for a particular month.

**Endpoint**

```http
POST /api/create-budget/
```

Example request:

```json
{
    "name": "August Budget",
    "amount": 100000,
    "month_year": "2026-08-01"
}
```

Example response:

```json
{
    "message": "Budget created successfully"
}
```

---

## Create Transaction

Creates a new income or expense transaction.

When an expense is created, the transaction amount is deducted from the budget's remaining balance.

When an income transaction is created, the transaction amount is added to the budget's remaining balance.

**Endpoint**

```http
POST /api/create-transactions/
```

Example expense transaction:

```json
{
    "type": "expenses",
    "amount": 5000,
    "category": 1,
    "description": "Groceries",
    "transaction_date": "2026-08-26"
}
```

Example recurring transaction:

```json
{
    "type": "expenses",
    "amount": 5000,
    "category": 1,
    "description": "Netflix subscription",
    "transaction_date": "2026-08-26",
    "frequency": "monthly"
}
```

Supported frequencies:

```text
weekly
monthly
yearly
```

---

## Delete Category

Deletes an existing category.

**Endpoint**

```http
DELETE /api/delete-category/id
```

The category to be deleted depends on the implementation of the `DeleteCategory` view.

---

# Recurring Transactions

The application supports recurring transactions.

A recurring transaction can have one of the following frequencies:

* Weekly
* Monthly
* Yearly

When a recurring transaction is created, a `next_occurence` date is calculated.

Example:

```text
Transaction created: August 26

Frequency: Weekly

Next occurrence:
September 2
```

The application uses Celery tasks to check whether a recurring transaction is due.

The recurring transaction flow works as follows:

```text
Celery Beat
    |
    | Runs scheduled task
    v
Celery Worker
    |
    v
Check recurring transactions
    |
    v
Is next_occurrence due?
    |
    +---- No ----> Ignore transaction
    |
    Yes
    |
    v
Process income or expense
    |
    v
Update budget remaining balance
    |
    v
Create transaction record
    |
    v
Move next_occurrence forward
```

For example, a weekly expense of ₦5,000 would be processed when its scheduled occurrence date is reached.

The budget's remaining balance is updated:

```text
Remaining Balance: ₦50,000
Recurring Expense: ₦5,000

New Remaining Balance: ₦45,000
```

The next occurrence is then moved forward by one week.

---

# Celery and Redis

Redis acts as the message broker between Django, Celery Beat, and the Celery worker.

The flow is:

```text
Django / Celery Beat
        |
        v
      Redis
        |
        v
  Celery Worker
        |
        v
 Execute Task
```

The Celery configuration uses Redis for both the broker and result backend.

Example configuration:

```python
CELERY_BROKER_URL = "redis://redis:6379/0"
CELERY_RESULT_BACKEND = "redis://redis:6379/0"
CELERY_TIMEZONE = "UTC"
CELERY_TASK_SERIALIZER = "json"
```

When running the project locally without Docker, `redis` can be replaced with `localhost`.

---

# Database Models

## Budget

The `Budget` model stores a user's monthly budget.

Key fields include:

```text
owner
name
amount
remaining_money
month_year
```

A user's budget keeps track of the original budget amount and the current remaining balance.

Example:

```text
Budget Amount: ₦100,000
Remaining Money: ₦100,000
```

After an expense:

```text
Expense: ₦20,000

Remaining Money: ₦80,000
```

Old budgets are retained to allow users to view their budgeting and transaction history.

---

## Transactions

The `Transactions` model stores both income and expense transactions.

Transaction types:

```text
income
expenses
```

A transaction belongs to a budget and contains information such as:

```text
owner
type
amount
category
description
transaction_date
budget
frequency
next_occurence
created_at
```

Transactions can also be configured as recurring transactions.

---

# Future Improvements

Possible improvements for the project include:

* Add transaction retrieval endpoints
* Add budget history endpoints
* Add monthly spending analytics
* Add category-based spending statistics
* Add budget limits and overspending validation
* Add transaction update endpoints
* Add transaction deletion endpoints
* Add API serializers for improved validation
* Add PostgreSQL for production use
* Add automated tests
* Add API documentation with Swagger or OpenAPI
* Add Docker volumes and production configuration
* Improve recurring transaction handling with a single periodic task that checks due transactions

## License

This project is available for learning and development purposes.
