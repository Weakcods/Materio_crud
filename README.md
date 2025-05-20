# Materio Dashboard Project

## Login Credentials
- Username: admin
- Password: admin123

## Overview
This is a Django-based dashboard application with various features including:
- Point of Sale (POS) system
- Analytics dashboard
- Product management
- Order management
- Customer management
- Table management
- Sales reporting

## Project Structure
- `apps/` - Contains all Django applications
- `config/` - Project configuration and settings
- `pos/` - Point of Sale system
- `static/` - Static files (CSS, JS, etc.)
- `templates/` - HTML templates
- `web_project/` - Core project files

## Getting Started

1. Create a virtual environment:
```bash
python -m venv myenv
```

2. Activate the virtual environment:
- Windows:
```bash
.\myenv\Scripts\activate
```
- Linux/Mac:
```bash
source myenv/bin/activate
```

3. Install requirements:
```bash
pip install -r requirements.txt
```

4. Run migrations:
```bash
python manage.py migrate
```

5. Start the development server:
```bash
python manage.py runserver
```

6. Access the application at `http://localhost:8000`

## Development
- Built with Django web framework
- Uses SQLite database by default
- Includes Gulp build system for frontend assets
