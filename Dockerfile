FROM python:3.9

# Augmenter le timeout et configurer pip
ENV PIP_DEFAULT_TIMEOUT=100
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PIP_NO_CACHE_DIR=1

ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE=ansade.settings

WORKDIR /app

# Installer les dépendances système pour MySQL
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copier les fichiers de dépendances
COPY requirements.txt /app/

# Utiliser --default-timeout pour pip
RUN pip install --default-timeout=100 --upgrade pip
RUN pip install --default-timeout=100 -r requirements.txt

# Copier le reste du projet
COPY . /app/

EXPOSE 23007

# CMD ["python", "manage.py", "runserver", "0.0.0.0:23007"]

# Ajouter à la fin du Dockerfile
COPY wait-for-it.sh /wait-for-it.sh
RUN chmod +x /wait-for-it.sh

CMD ["/wait-for-it.sh", "db:3306", "--", "python", "manage.py", "runserver", "0.0.0.0:23007"]