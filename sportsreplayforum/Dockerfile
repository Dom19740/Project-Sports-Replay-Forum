FROM python:3.11.4-slim-bullseye
WORKDIR /sportsreplayforum

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY ./requirements.txt /sportsreplayforum/
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Copy the project files
COPY . /sportsreplayforum

# Collect static files
RUN python manage.py collectstatic --noinput

# Start the Gunicorn server
ENTRYPOINT ["gunicorn", "sportsreplayforum.wsgi:application", "-b", "0.0.0.0:8000"]
