FROM python:3.8
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
WORKDIR /app
COPY backend/ ./
RUN pip install setuptools==40
RUN pip install -r /app/requirements.txt
RUN apt-get update && apt-get install -y systemd wkhtmltopdf && rm -rf /var/lib/apt/lists/*
CMD ["gunicorn", "exchange.wsgi:application", "-b", "0.0.0.0:8080", "-w", "2", "--access-logfile", "-", "--error-logfile", "-"]
