---

# Flask React REST API Application

This is a REST API application built with Flask. The project includes user management, prompt management, and various functionalities as described in the database schema.

## Features

- User Authentication, Activation and Authorization
- Prompt Management
- Group Management
- Vote and Note System
- Automated Database Management
- Role-Based Access Control with Decorators
- OpenAPI Documentation for the API

## Requirements

- Python 3.7+
- Flask
- Flask-Smorest
- Flask-JWT-Extended
- PostgreSQL
- Psycopg

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/soszaboss/prompt-management-system.git
cd yourproject
```
### 2. Run the application

To start the Flask development server, run:

```bash
flask run
```

### 3. Create a virtual environment and activate it

```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

### 4. Install the dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure the database

Ensure that you have PostgreSQL installed and create a database for your project. Update the database configuration in the `config.py` file.

### 6. Initialize the database

To initialize the database with the required tables and functions, run:

```bash
flask init-db
```

This command will execute the SQL script to set up the database schema.

### 7. Create a superuser

To create a superuser, run:

```bash
flask createsuperuser
```

Follow the prompts to enter the username, email, and password for the superuser.

The application will be accessible at `http://127.0.0.1:5000/`.

## Project Structure

- `app/` - Contains the Flask application and modules
- `tests/` - Unit tests
- `config.py` - Configuration file
- `schema.sql` - SQL script for database schema

## Available Commands

- `flask run` - Starts the Flask development server
- `flask init-db` - Initializes the database
- `flask createsuperuser` - Creates a superuser

## Testing

- The application includes unit tests to ensure the proper functioning of various features. You can run the tests using:

```bash
pytest
```

- The test suite includes coverage for endpoints like user authentication, prompt management, and voting. It also validates that access control decorators are correctly enforcing role-based access restrictions.

## Role-Based Access Control

- The application uses custom decorators to enforce role-based access to specific routes. For example, the `@users_allowed(['admin', 'user'])` decorator restricts access to routes based on the user's role. If a user does not have the required privilege, they will not be able to access the route.

## API Documentation

- The application provides OpenAPI documentation available at the `/swagger-ui` URL. This documentation allows you to explore and test the API endpoints directly from your browser.

## Acknowledgments

- Flask Documentation
- PostgreSQL Documentation

---

This README provides a comprehensive guide to setting up, initializing, and running your Flask React REST API application. You can customize it further as per your project's requirements.
