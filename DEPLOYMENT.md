# Deployment Guide

This guide explains how to deploy the PDF Generator application using Docker.

## Prerequisites

- [Docker](https://www.docker.com/get-started) installed on your machine.
- A Gemini API Key from Google AI Studio.

## Setup & Run

1.  **Set Environment Variables**
    Create a `.env` file in the root directory (where `docker-compose.yml` is) and add your Gemini API key:
    ```env
    GEMINI_API_KEY=your_actual_api_key_here
    ```

2.  **Build and Run**
    Run the following command to build the images and start the containers:
    ```bash
    docker-compose up --build -d
    ```

3.  **Access the Application**
    Open your browser and navigate to:
    [http://localhost](http://localhost)

## Architecture

- **Frontend**: React app served via Nginx (Port 80).
- **Backend**: FastAPI app (Internal Port 8000).
- **Database**: MongoDB (Internal Port 27017).

## Troubleshooting

-   **Backend Connection**: If the frontend cannot connect to the backend, ensure the `backend` service is running and checking the browser console for errors. Nginx is configured to proxy `/api` requests to the backend container.
-   **Gemini API Error**: Check backend logs (`docker logs pdf-generator-backend`) to ensure the API key is valid.

## Stopping the App

To stop the containers:
```bash
docker-compose down
```
