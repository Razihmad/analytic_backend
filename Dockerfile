# Use an official Python image
FROM python:3.12-slim

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    ln -s /root/.local/bin/poetry /usr/local/bin/poetry

# Copy only necessary files for Poetry installation
COPY pyproject.toml poetry.lock ./

# Install dependencies using Poetry
RUN poetry config virtualenvs.create false && poetry install --no-root --no-interaction --no-ansi

# Copy the Django project files into the container
COPY . .

# Expose the port the Django app runs on
EXPOSE 8000

# Run the Django development server by default (adjust as needed for production)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
