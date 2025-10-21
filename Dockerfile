FROM python:3.11-slim

WORKDIR /app

# Install required packages for creating sample content
RUN pip install --no-cache-dir reportlab Pillow

# Copy server and client scripts
COPY server.py .
COPY client.py .
COPY setup_content.py .

# Create content directory
RUN mkdir -p /app/content

# Make scripts executable
RUN chmod +x server.py client.py

# Expose the server port
EXPOSE 8080

# Set Python to run in unbuffered mode
ENV PYTHONUNBUFFERED=1

# Default command runs the server
CMD ["python", "-u", "server.py", "/app/content", "8080"]