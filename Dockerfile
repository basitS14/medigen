# Use an official Python runtime as a base image
FROM python:3.12.5

# Set the working directory in the container
WORKDIR /app

# Copy requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project to the container
COPY . .

# Expose port 8000 for Django
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run Django server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
