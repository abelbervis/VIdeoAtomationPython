FROM python:3.10-slim

# Install system dependencies (FFmpeg with libass and fonts for subtitles)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    fonts-dejavu-core \
    fonts-freefont-ttf \
    fonts-wqy-zenhei \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create volume mount targets
RUN mkdir -p /app/assets/music /app/assets/sfx/intro /app/assets/sfx/swoosh /app/output /app/audio /app/subtitles /app/temp

ENTRYPOINT ["python", "main.py"]
CMD ["--help"]
