# PDF Generator App

This project consists of a Python FastAPI backend and a React frontend, using MongoDB as the database.

## Prerequisites

- [Docker](https://www.docker.com/products/docker-desktop) and [Docker Compose](https://docs.docker.com/compose/install/) (Recommended)
- **OR**
- [Python 3.10+](https://www.python.org/downloads/)
- [Node.js 16+](https://nodejs.org/)
- [MongoDB](https://www.mongodb.com/try/download/community) locally installed or a cloud instance.

## Option 1: Docker Compose (Recommended)

The easiest way to run the application is using Docker Compose.

1.  **Create a `.env` file** in the root directory (or ensure you have the variable set in your shell):
    ```env
    GEMINI_API_KEY=your_api_key_here
    ```

2.  **Build and Run**:
    Open a terminal in the project root and run:
    ```bash
    docker-compose up --build
    ```

3.  **Access the App**:
    - Frontend: [http://localhost:80](http://localhost:80)
    - Backend Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

## Option 2: Manual Setup

If you prefer to run services individually without Docker:

### 1. Database

Ensure you have a MongoDB instance running locally on port `27017` or have a connection string ready.

### 2. Backend

1.  Navigate to the backend directory:
    ```bash
    cd backend
    ```

2.  Create and activate a virtual environment:
    ```bash
    # Windows
    python -m venv venv
    .\venv\Scripts\activate

    # macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4.  Set Environment Variables and Run:
    You need to set `MONGO_URL`, `DB_NAME`, and `GEMINI_API_KEY`.

    **Windows (PowerShell):**
    ```powershell
    $env:MONGO_URL="mongodb://localhost:27017/pdf_app"
    $env:DB_NAME="pdf_app"
    $env:GEMINI_API_KEY="your_api_key_here"
    $env:CORS_ORIGINS="http://localhost:3000"

    uvicorn server:app --host 0.0.0.0 --port 8000 --reload
    ```

    **macOS/Linux:**
    ```bash
    export MONGO_URL="mongodb://localhost:27017/pdf_app"
    export DB_NAME="pdf_app"
    export GEMINI_API_KEY="your_api_key_here"
    export CORS_ORIGINS="http://localhost:3000"

    uvicorn server:app --host 0.0.0.0 --port 8000 --reload
    ```

    The backend should now be running at `http://localhost:8000`.

### 3. Frontend

1.  Navigate to the frontend directory:
    ```bash
    cd frontend
    ```

2.  Install dependencies:
    ```bash
    npm install
    # OR
    yarn install
    ```

3.  Start the development server:
    ```bash
    npm start
    ```

    The frontend should open automatically at `http://localhost:3000`.
