FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    STREAMLIT_CONFIG_DIR=/app/.streamlit

WORKDIR /app

RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

COPY . /app
COPY frontend/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

RUN pip install --upgrade pip && pip install -r requirements.txt

EXPOSE 8501

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["streamlit", "run", "frontend/main.py"]
