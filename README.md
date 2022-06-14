[![Python application](https://github.com/biratkdk/django-todos/actions/workflows/python-app.yml/badge.svg)](https://github.com/biratkdk/django-todos/actions/workflows/python-app.yml)
[![codecov](https://codecov.io/gh/biratkdk/django-todos/branch/main/graph/badge.svg?token=1QyMooGbYZ)](https://codecov.io/gh/biratkdk/django-todos)

# Django Todos

A multi-user Django todo application with account registration, email verification, login/logout, and a richer personal task dashboard.

## Features

- Custom user model for authentication.
- Email-based account activation flow with form-based validation.
- Create, view, edit, and delete personal todos.
- Track priority, due dates, and completion timestamps.
- Search todos by title or description.
- Filter todos by completion status, overdue work, due-soon items, and high priority.
- User-scoped access so one user cannot access another user's todos.
- Custom 404 and 500 pages.
- Test coverage for authentication and todo flows.

## Stack

- Python 3.11
- Django
- SQLite for local development
- PostgreSQL via `DATABASE_URL` for deployed environments
- Gunicorn
- WhiteNoise
- GitHub Actions

## Project Structure

```text
authentication/   User model, auth views, activation flow, auth tests
helpers/          Shared helpers, decorators, custom error handlers
static/           Static source assets
templates/        HTML templates for auth, todo pages, and shared partials
todo/             Todo model, forms, views, routes, and tests
todosite/         Project settings, URL routing, ASGI/WSGI entrypoints
utils/            Test setup utilities
```

## Quick Start

### 1. Clone and create a virtual environment

```powershell
git clone https://github.com/biratkdk/django-todos.git
cd django-todos
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```powershell
pip install -r requirements.txt
```

### 3. Configure environment variables

Copy `.env-sample` into your own local env file or export the variables in your shell.

Example values:

```env
SECRET_KEY=change-me
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
DATABASE_URL=
EMAIL_FROM_USER=
EMAIL_BACKEND=
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
CSRF_TRUSTED_ORIGINS=
```

### 4. Run migrations and start the server

```powershell
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open `http://127.0.0.1:8000/`.

## Main Routes

- `/` : dashboard with the current user's todos
- `/create/` : create a new todo
- `/todo/<id>/` : view a single todo
- `/edit-todo/<id>/` : edit a todo
- `/todo-delete/<id>/` : delete a todo
- `/auth/register` : register a new account
- `/auth/login` : log in
- `/auth/logout_user` : log out
- `/auth/activate-user/<uidb64>/<token>` : activate an account from email

Useful query params on `/`:

- `?q=database` : search title and description
- `?filter=incomplete` : show open work
- `?filter=complete` : show completed work
- `?filter=overdue` : show overdue items
- `?filter=due-soon` : show tasks due in the next 7 days
- `?filter=high-priority` : show open high-priority tasks

## Development Notes

- If `DATABASE_URL` is not set, the app uses local SQLite.
- If `EMAIL_BACKEND` is not set, development uses Django's console email backend and production uses SMTP.
- In production, set `DEBUG=False`, `DATABASE_URL`, `ALLOWED_HOSTS`, and `CSRF_TRUSTED_ORIGINS`.
- Static files are served from `static/` in development and can be collected for deployment.

## Running Tests

```powershell
python manage.py test
```

To run coverage locally:

```powershell
coverage run manage.py test
coverage report
```

## Deployment

This repo includes a `Procfile` and is ready for WSGI deployment with Gunicorn. Before deploying:

- set a secure `SECRET_KEY`
- configure `DATABASE_URL`
- configure email credentials for account activation
- run `python manage.py migrate`
- run `python manage.py collectstatic`

## Current Behavior

- New users register and receive an activation email.
- Only verified users can log in.
- Todos are private to the signed-in user.
- Todo list filtering supports complete, incomplete, overdue, due-soon, and high-priority items through query params.
- Todos can store due dates, priority levels, and completion timestamps.
