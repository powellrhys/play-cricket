# syntax=docker/dockerfile:1.4
# Use python list base image
FROM python:3.13-slim

# Define environmental variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    STREAMLIT_CONFIG_DIR=/app/.streamlit

# Setup working directory
WORKDIR /app

# Install system dependencies (git required for pip install from GitHub)
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Copy project into the image
COPY . /app

# Install Python dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Use BuildKit to securely copy secret.toml into .streamlit
RUN --mount=type=secret,id=secret_toml \
    mkdir -p /app/.streamlit && \
    cp /run/secrets/secret_toml /app/.streamlit/secret.toml

# Expose Streamlit's default port
EXPOSE 8501

# Launch the Streamlit app
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
