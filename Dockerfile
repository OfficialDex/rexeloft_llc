# Base image with Python
FROM python:3.9-slim

# Install system dependencies for Chrome
RUN apt-get update && apt-get install -y wget gnupg unzip \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list' \
    && apt-get update && apt-get install -y google-chrome-stable \
    && echo "Google Chrome installed"

# Set environment variables for Chrome and Selenium
ENV DISPLAY=:99
ENV CHROME_BIN=/usr/bin/google-chrome

# Copy project files
WORKDIR /app
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port Flask will run on
EXPOSE 5000

# Start the Flask app
CMD ["python", "main.py"]
