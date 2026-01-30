# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
# Install system dependencies for pycairo, WeasyPrint, and LaTeX
RUN apt-get update && apt-get install -y \
    build-essential \
    pkg-config \
    python3-dev \
    python3-pip \
    python3-setuptools \
    python3-wheel \
    python3-cffi \
    libcairo2 \
    libcairo2-dev \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    libffi-dev \
    shared-mime-info \
    texlive-latex-base \
    texlive-latex-extra \
    texlive-fonts-recommended \
    texlive-fonts-extra \
    texlive-xetex \
    texlive-luatex \
    texlive-science \
    cm-super \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt ./requirements.txt

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend code to /app/backend to preserve module structure
COPY . ./backend

# Expose port 8000
EXPOSE 8000

# Run the application from /app with backend.server module path
CMD ["uvicorn", "backend.server:app", "--host", "0.0.0.0", "--port", "8000"]
