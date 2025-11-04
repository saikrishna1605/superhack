# Quick Start Guide - PulseOps AI Platform

This guide will help you get the PulseOps AI platform up and running locally with minimal effort.

## Prerequisites

1. Python 3.8+ installed
2. Node.js 14+ and npm installed
3. PostgreSQL installed and running (if using local database)

## Step 1: Backend Setup (FastAPI)

1. Navigate to the API directory:
   ```bash
   cd services/api
   ```

2. Create and activate a Python virtual environment (recommended):
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate

   # Linux/Mac
   python -m venv venv
   source venv/bin/activate
   ```

3. Install required Python packages:
   ```bash
   pip install fastapi uvicorn sqlalchemy pydantic python-jose[cryptography] passlib[bcrypt] python-multipart alembic psycopg2-binary mangum pydantic-settings email-validator
   ```

4. Start the backend server:

   > Note: By default, the application uses SQLite database. If you want to use PostgreSQL instead, 
   > refer to the configuration guide in `services/api/README.md`.

   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

   The API will be available at:
   - Main API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Alternative API Docs: http://localhost:8000/redoc

## Step 2: Frontend Setup (React)

1. Open a new terminal and navigate to the UI directory:
   ```bash
   cd services/ui
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm start
   ```

   The UI will automatically open in your default browser at http://localhost:3000

## Demo Credentials

Use these credentials to log in:
- **MSP User**: demo-msp@example.com / password123
- **IT Admin**: demo-it@example.com / password123

## Verifying the Setup

1. Backend verification:
   - Open http://localhost:8000/docs in your browser
   - You should see the SwaggerUI documentation

2. Frontend verification:
   - Open http://localhost:3000 in your browser
   - You should see the login page
   - Try logging in with the demo credentials

## Troubleshooting

### Backend Issues
1. If you see "module not found" errors, ensure you've installed all packages:
   ```bash
   pip install -r requirements.txt
   ```

2. Database connection issues:
   - Verify PostgreSQL is running
   - Check environment variables are set correctly
   - Ensure database exists and is accessible

### Frontend Issues
1. Port 3000 already in use:
   - Accept the prompt to use a different port
   - Or kill the process using port 3000 and restart

2. NPM vulnerabilities warning:
   ```bash
   npm audit fix
   # If needed, use force:
   npm audit fix --force
   ```

## Stopping the Application

1. Stop the frontend:
   - Press Ctrl+C in the terminal running the React server

2. Stop the backend:
   - Press Ctrl+C in the terminal running uvicorn

## Additional Resources

- Backend API documentation in `services/api/README.md`
- Frontend documentation in `services/ui/README.md`
- Full deployment guide in `DEPLOYMENT_GUIDE.md`