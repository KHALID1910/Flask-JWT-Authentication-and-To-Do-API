# Flask JWT Authentication and To-Do API

This repository contains a Flask application that provides authentication using JWT (JSON Web Tokens) and allows users to manage to-do tasks. The application has the following features:

- User registration and management.
- Login authentication with JWT.
- Token-based access control.
- CRUD operations for to-do tasks.

## Features

### User Management
- **Create User**: Register a new user.
- **Promote User**: Grant admin privileges to a user (admin only).
- **Delete User**: Remove a user from the system (admin only).
- **List Users**: View all users (admin only).
- **Get User by ID**: Fetch details of a specific user (admin only).

### To-Do Management
- **Create To-Do**: Add a new to-do item.
- **View To-Dos**: Fetch all to-do items for the current user.
- **View Single To-Do**: Fetch details of a specific to-do item.
- **Mark To-Do as Completed**: Update the status of a to-do item.
- **Delete To-Do**: Remove a to-do item.

### Authentication
- JWT-based authentication for secure access.
- Admin-only routes for managing users.

## Getting Started

### Prerequisites
- Python 3.x
- Flask
- SQLite (default database)
- OR RUN COMMAND:
  - pip install requirements.txt

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/flask-jwt-todo.git
   cd flask-jwt-todo
   ```
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Initialize the database:
   ```bash
   python
   >>> from app import db
   >>> db.create_all()
   >>> exit()
   ```
5. Run the application:
   ```bash
   python app.py
   ```
   The application will be accessible at `http://127.0.0.1:8000/`.

### Routes

#### Authentication
- **`/login`** (GET): Login to obtain a JWT token.

#### User Management
- **`/user`** (POST): Register a new user.
- **`/user`** (GET): List all users (admin only).
- **`/user/<public_id>`** (GET): Get details of a user by `public_id` (admin only).
- **`/user/<public_id>`** (PUT): Promote a user to admin (admin only).
- **`/user/<public_id>`** (DELETE): Delete a user (admin only).

#### To-Do Management
- **`/todo`** (GET): Fetch all to-do items for the current user.
- **`/todo/<todo_id>`** (GET): Fetch details of a specific to-do item.
- **`/todo`** (POST): Create a new to-do item.
- **`/todo/<todo_id>`** (PUT): Mark a to-do item as completed.
- **`/todo/<todo_id>`** (DELETE): Delete a to-do item.

### Request and Response Examples

#### Login
**Request**:
```bash
curl -u username:password http://127.0.0.1:8000/login
```
**Response Generated Token**:
```json
{
  "token": "your-jwt-token"
}
```

#### Create User
**Request**:
```bash
curl -X POST http://127.0.0.1:8000/user -H "Content-Type: application/json" -d '{"name": "John", "password": "12345"}'
```
**Response**:
```json
{
  "message": "user created successfully!!"
}
```

#### Fetch All To-Dos
**Request**:
```bash
curl -X GET http://127.0.0.1:8000/todo -H "x-access-token: your-jwt-token"
```
**Response**:
```json
{
  "todos": [
    {
      "id": 1,
      "text": "Sample task",
      "completed": false
    }
  ]
}
```

### Environment Variables
- `SECRET_KEY`: Secret key for encoding JWT tokens.
- `SQLALCHEMY_DATABASE_URI`: Database URI (default: SQLite).

## Technologies Used

- **Python**: Core programming language for the application.
- **Flask**: Micro web framework used for creating APIs and managing routes.
- **JWT Authentication**: Secure user authentication and session management.
- **Flask-SQLAlchemy**: ORM (Object Relational Mapper) for database interaction.
- **SQLite**: Lightweight database for storing user and todo data.
- **Werkzeug Security**: Secure password hashing and verification.
- **Postman**: API testing and debugging tool.
- **HTTP Methods**: Core API operations (GET, POST, PUT, DELETE).

