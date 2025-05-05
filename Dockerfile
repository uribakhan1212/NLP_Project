FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

# Install Python and other dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.10 \
    python3-pip \
    python3.10-dev \
    python3.10-venv \
    build-essential \
    gcc \
    g++ \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set python3 as default
RUN ln -s /usr/bin/python3.10 /usr/bin/python

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install pip requirements (except torch, torchaudio, torchvision)
COPY requirements1.txt .
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements1.txt
# Install CUDA-enabled PyTorch
RUN pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

WORKDIR /app
COPY . /app

EXPOSE 50052

RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

CMD ["python3", "NLP_Project/main.py"]
