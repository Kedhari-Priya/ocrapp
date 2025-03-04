# Use an official lightweight Python image
FROM python:3.11

# Install Tesseract
RUN apt-get update && apt-get install -y tesseract-ocr

# Set the working directory in the container
WORKDIR /app

# Copy all files from your repository into the container
COPY . /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose Streamlit default port
EXPOSE 8501

# Run the Streamlit app
CMD ["streamlit", "run", "app.py", "--server.port=10000", "--server.address=0.0.0.0"]
