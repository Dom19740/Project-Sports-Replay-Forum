FROM python:3.11.4-slim-bullseye
WORKDIR /sportsreplayforum

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# install system dependencies
RUN apt-get update

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt /sportsreplayforum/
RUN pip install -r requirements.txt

COPY . /sportsreplayforum

# Run collectstatic during build
RUN python manage.py collectstatic --noinput

ENTRYPOINT [ "gunicorn", "sportsreplayforum.wsgi", "-b", "0.0.0.0:8000"]