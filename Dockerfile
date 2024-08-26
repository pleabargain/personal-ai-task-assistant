# Dockerfile
FROM python:3.10-slim

# Install required system dependencies, fonts, and font tools
# RUN apt-get update && apt-get install -y \
#     wget \
#     git \
#     gcc \
#     fonts-liberation \
#     fontconfig \
#     && rm -rf /var/lib/apt/lists/*

# Update font cache
# RUN fc-cache -f -v

# Create necessary directories and symlinks for fonts
# RUN mkdir -p /usr/share/fonts/truetype/msttcorefonts \
#     && ln -s /usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf /usr/share/fonts/truetype/msttcorefonts/Arial.ttf

# Set working directory
WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Run the application
CMD ["streamlit", "run", "src/app.py", "--server.port=8080", "--server.enableCORS=false"]