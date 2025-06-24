FROM python:3.13-slim

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


# # Use python list base image
# FROM python:3.13-slim

# # Define environmental variables
# ENV PYTHONDONTWRITEBYTECODE=1 \
#     PYTHONUNBUFFERED=1

# # Setup working directory
# WORKDIR /app

# # Install system dependencies (git required for pip install from GitHub)
# RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# # Copy from the context (root) into the image
# COPY . /app

# # Install project dependencies
# RUN pip install --upgrade pip && pip install -r requirements.txt

# # Expose port 8501
# EXPOSE 8501

# # Define project environmental variables
# ENV STREAMLIT_CONFIG_DIR=/app/.streamlit

# # Define initialize command
# CMD ["streamlit", "run", "frontend/main.py"]
