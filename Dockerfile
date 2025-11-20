# Use Python 3.10 so mediapipe is happy
FROM python:3.10-slim

# Install system libraries needed by OpenCV / mediapipe
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Workdir inside the container
WORKDIR /app

# Copy requirements and install
COPY AntiDote/ANTIDOTE/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the actual app code
COPY AntiDote/ANTIDOTE ./ANTIDOTE

# Expose Streamlit port
EXPOSE 8501

# Run your main Streamlit app
CMD ["streamlit", "run", "ANTIDOTE/Home.py", "--server.port=8501", "--server.address=0.0.0.0"]
