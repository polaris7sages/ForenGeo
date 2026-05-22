FROM python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

COPY requirements.txt ./
RUN python -m pip install --upgrade pip && pip install -r requirements.txt

COPY . .
RUN useradd --create-home --shell /bin/bash forengeo && chown -R forengeo:forengeo /app
USER forengeo

EXPOSE 5000
CMD ["python", "fh3_cli.py", "init"]