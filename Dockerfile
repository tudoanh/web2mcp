# Use an official Python runtime as a parent image
FROM python:3.12

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install uv - faster Python package installer
ADD --chmod=755 https://astral.sh/uv/install.sh /install.sh
RUN /install.sh && rm /install.sh

# Install dependencies using uv
# Copy only requirements first to leverage Docker cache
COPY requirements.txt .
RUN /root/.local/bin/uv pip install --no-cache -r requirements.txt --system

# Copy project code
COPY . .

# Expose port 8008
EXPOSE 8008

# Run database migrations and start server
# Note: Running migrations here assumes the DB is available when the container starts.
# For production, migrations are often run as a separate step or entrypoint script.
CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8008"]
