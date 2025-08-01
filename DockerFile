# Use a lightweight Python image
FROM python:3.10-slim

# Set working directory inside container
WORKDIR /app

# Copy dependency list and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your Flask app code
COPY . .

# Start the app using Gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:8080", "app:app"]
