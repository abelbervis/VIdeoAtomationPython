FROM python:3.10-slim

# Install system dependencies (FFmpeg with libass, fonts, curl and Node.js)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    fonts-dejavu-core \
    fonts-freefont-ttf \
    fonts-wqy-zenhei \
    ca-certificates \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Node.js dependencies
COPY package*.json ./
RUN npm install

# Copy project files
COPY . .

# Build web application bundle
RUN npm run build

# Create required volume mount targets
RUN mkdir -p /app/assets/music /app/assets/sfx/intro /app/assets/sfx/swoosh /app/assets/orbs /app/output /app/audio /app/subtitles /app/temp

EXPOSE 3000

ENV PORT=3000
ENV NODE_ENV=production

CMD ["npm", "start"]

