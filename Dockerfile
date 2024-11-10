# Base image with Python
FROM python:3.9-slim

# Install system dependencies for Chrome and Selenium
RUN apt-get update && apt-get install -y wget gnupg unzip \
    && echo "System dependencies installed" \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "Google signing key added" \
    && sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list' \
    && apt-get update && apt-get install -y google-chrome-stable \
    && echo "Google Chrome installed" \
    && wget -O /tmp/chromedriver.zip https://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_linux64.zip \
    && echo "Chromedriver downloaded" \
    && unzip /tmp/chromedriver.zip -d /usr/local/bin/ \
    && rm /tmp/chromedriver.zip \
    && echo "Chromedriver installed"

# Verify Chrome and Chromedriver installations
RUN echo "Verifying Chrome installation" && google-chrome --version \
    && echo "Verifying Chromedriver installation" && ls -l /usr/local/bin/chromedriver

# Set environment variables for Chrome and Selenium
ENV DISPLAY=:99
ENV CHROME_BIN=/usr/bin/google-chrome
ENV CHROMEDRIVER_PATH=/usr/local/bin/chromedriver

# Copy project files
WORKDIR /app
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt \
    && echo "Python dependencies installed"

# Expose the port Flask will run on
EXPOSE 5000

# Start the Flask app
CMD ["python", "app.py"]
