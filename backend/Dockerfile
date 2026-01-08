FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
# texlive for pdflatex
# libcairo2-dev and pkg-config for xhtml2pdf (via pycairo)
RUN apt-get update && apt-get install -y \
    texlive-latex-base \
    texlive-fonts-recommended \
    texlive-latex-extra \
    texlive-fonts-extra \
    libcairo2-dev \
    pkg-config \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY requirements.txt .

# Install python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 10000

# Start command
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "10000"]
