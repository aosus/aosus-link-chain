# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file first to leverage Docker cache
# For the matrix bot, dependencies are matrix-nio and python-dotenv
# We'll create a minimal requirements_matrix.txt for this Dockerfile
# Or, if requirements.txt is kept lean and only includes these, it can be used.
# For now, let's assume we'll install them directly.

# Copy the local directory contents to the container at /app
COPY matrix_bot.py .
COPY sample.config/ ./sample.config/

# Install any needed packages specified in requirements.txt
# For matrix_bot.py, the specific dependencies are matrix-nio and python-dotenv
RUN pip install --no-cache-dir matrix-nio python-dotenv

# Create a non-root user and group
RUN groupadd -r appgroup && useradd --no-log-init -r -g appgroup appuser

# Ensure the /app directory and its contents are owned by the new user
# This is important if sample.config files need to be read by the default mechanism
# or if the bot itself tries to write to /app (though it shouldn't by default)
RUN chown -R appuser:appgroup /app

# Switch to the non-root user
USER appuser

# Make port 80 available to the world outside this container (if needed, not for this bot)
# EXPOSE 80

# Define environment variable
# ENV NAME World

# Run matrix_bot.py when the container launches
CMD ["python", "matrix_bot.py"]
