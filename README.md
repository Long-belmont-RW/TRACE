# TRACE

Welcome to **TRACE**. This is a Django-based web application designed for managing and tracking information related to custody and judicial processes. 

## Project Overview

TRACE is built to be a secure and robust platform. Our key domains are divided into specific Django apps:
* **`accounts`**: User management, authentication, and profiles. We utilize Two-Factor Authentication (2FA) for enhanced security.
* **`custody`**: Management of custody records and related data.
* **`judiciary`**: Handling of judicial records, court information, and proceedings.

## Tech Stack

* **Backend**: Django 5.0+, Python 3.8+
* **Frontend**: Tailwind CSS (v4)
* **Asynchronous Tasks**: Celery & Redis
* **Security**: django-two-factor-auth, django-otp

## Getting Started

### Prerequisites

Please ensure you have the following installed on your local development machine:
* **Python 3.8+**
* **Node.js & npm** (for Tailwind CSS)
* **Redis server** (running locally or via Docker for Celery tasks)

### Backend Setup

1. **Clone the repository** (if you haven't already) and navigate to the project root:
   ```bash
   git clone https://github.com/Long-belmont-RW/TRACE.git
   cd TRACE
   ```

2. **Create and activate a virtual environment**:
   * **Windows:**
     ```bash
     python -m venv venv
     venv\Scripts\activate
     ```
   * **macOS/Linux:**
     ```bash
     python -m venv venv
     source venv/bin/activate
     ```

3. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables**:
   * Create a `.env` file in the root directory.
   * Add the required environment variables. You will need at least:
     ```env
     SECRET_KEY=your-secret-key
     DEBUG=True
     # Add database credentials and Redis URL if different from defaults
     ```

5. **Apply Database Migrations**:
   ```bash
   python manage.py migrate
   ```

6. **Create a Superuser** (for accessing the Django admin interface):
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the Development Server**:
   ```bash
   python manage.py runserver
   ```

### Frontend Setup (Tailwind CSS)

We use Tailwind CSS for styling. To compile the CSS during development:

1. **Install Node.js dependencies**:
   ```bash
   npm install
   ```

2. **Start the Tailwind CSS watcher**:
   This will watch for changes in your HTML templates and rebuild the CSS automatically.
   ```bash
   npm run watch:css
   ```
   *(To build for production, use `npm run build:css`)*

### Background Tasks (Celery & Redis)

Some processes in TRACE are handled asynchronously using Celery.

1. Ensure your **Redis server** is running.
2. In a separate terminal (with your virtual environment activated), start the Celery worker:
   * **Windows** (may require `gevent` or `eventlet`):
     ```bash
     celery -A config worker -l info -P eventlet
     ```
   * **macOS/Linux**:
     ```bash
     celery -A config worker -l info
     ```

## Project Structure

* `apps/` - Contains the core Django applications (`accounts`, `custody`, `judiciary`).
* `config/` - Project-level configuration settings, URLs, and ASGI/WSGI entry points.
* `static/` - Static assets (CSS, JS, images). Source CSS for Tailwind is in `static/src/`.
* `templates/` - Global HTML templates. App-specific templates should go inside their respective app directories.

## Contributing

When picking up a new task, please ensure you branch off `main` and submit a Pull Request for review.
