# TRACE

A Django project.

## Getting Started

### Prerequisites

* Python 3.8+
* Virtual Environment (recommended)

### Installation

1. Clone the repository or navigate to the project directory.

2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:
   * **Windows:**
     ```bash
     venv\Scripts\activate
     ```
   * **macOS/Linux:**
     ```bash
     source venv/bin/activate
     ```

4. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Set up the environment variables:
   * Create a `.env` file in the root directory.
   * Add necessary environment variables (like `SECRET_KEY`, database credentials, etc.) according to your configuration requirements.

6. Apply database migrations:
   ```bash
   python manage.py migrate
   ```

7. Run the development server:
   ```bash
   python manage.py runserver
   ```

## Structure
* `apps/` - Django applications.
* `config/` - Project configuration settings.
* `templates/` - HTML templates.
