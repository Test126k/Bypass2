# Use an official Python runtime as a parent image
   FROM python:3.9-slim

   # Set the working directory in the container
   WORKDIR /app

   # Copy the requirements file into the container
   COPY requirements.txt .

   # Install dependencies
   RUN pip install --no-cache-dir -r requirements.txt

   # Install Playwright and its browsers
   RUN playwright install

   # Copy the rest of the application code
   COPY . .

   # Expose the port the app runs on
   EXPOSE 8080

   # Run the bot
   CMD ["python", "bot.py"]
