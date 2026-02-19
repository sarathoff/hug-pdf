# Use Debian Bullseye for better pip wheel compatibility
FROM python:3.11-bullseye

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    cmake \
    pkg-config \
    python3-dev \
    python3-cffi \
    python3-cairo \
    libcairo2 \
    libcairo2-dev \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    libffi-dev \
    zlib1g-dev \
    libzopfli-dev \
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

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt ./requirements.txt

# Install C-extension packages first (so headers are available), then the rest
RUN pip install --no-cache-dir --upgrade pip setuptools wheel \
    && pip install --no-cache-dir pycairo \
    && pip install --no-cache-dir zopfli \
    && pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY . ./backend

# Expose port
EXPOSE 8000

# Start server
CMD ["uvicorn", "backend.server:app", "--host", "0.0.0.0", "--port", "8000"]
