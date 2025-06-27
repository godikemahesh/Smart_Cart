FROM python:3.10-slim

# System packages for Playwright + Headless Chrome
RUN apt-get update && apt-get install -y \
    curl unzip wget gnupg libnss3 libatk1.0-0 libxss1 \
    libasound2 libxshmfence1 libgbm-dev \
    && apt-get clean

# Create app directory
WORKDIR /app

# Copy all project files
COPY . .

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Install Playwright and Chromium
RUN playwright install --with-deps

# Expose Streamlit's default port
EXPOSE 8501

# Start Streamlit app
CMD ["streamlit", "run", "smartcart/main2.py", "--server.port=8501", "--server.enableCORS=false"]
