# Use the specified Python 3.9 slim image
FROM python:3.9-slim@sha256:980b778550c0d938574f1b556362b27601ea5c620130a572feb63ac1df03eda5

# Ensure the Python output is not buffered
ENV PYTHONUNBUFFERED=True

# Set the working directory in the container
ENV APP_HOME=/app
WORKDIR $APP_HOME

# Copy all the application files to the working directory
COPY . ./



# Set the port environment variable
ENV PORT=8080

# Install the required Python packages
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Command to run the web service with uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
