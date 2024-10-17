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

# Optionally copy already collected static files
COPY ./staticfiles /sportsreplayforum/staticfiles  # Ensure this matches where you have collected them

# Start the Gunicorn server
ENTRYPOINT ["gunicorn", "sportsreplayforum.wsgi:application", "-b", "0.0.0.0:8000"]
