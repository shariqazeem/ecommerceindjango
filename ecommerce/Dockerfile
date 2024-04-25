# Use the official Python image as base image
FROM python:3.10

# Set environment variables
ENV DJANGO_SETTINGS_MODULE=ecommerce.settings
ENV DJANGO_DEBUG=False

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

RUN pip install gunicorn

RUN python manage.py collectstatic --no-input

# Expose the port the app runs on
EXPOSE 8000

# Run the Django app
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "ecommerce.wsgi:application"]
