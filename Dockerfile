# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application's code from your computer to the container
COPY . .

# Expose the port the app runs on (Hugging Face Spaces default is 7860)
EXPOSE 7860

# Define the command to run your app using gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:7860", "app:app"]