# official Python (Alpine Linux) runtime
FROM python:alpine

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN apk add --no-cache gcc python3-dev musl-dev linux-headers

RUN pip install --no-cache-dir -r requirements.txt && \
    apk add --no-cache supervisor && \
    rm -rf /var/cache/apk/*

# Make port 8000 available to the world outside this container
EXPOSE 8000

COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Run supervisord when the container launches
CMD ["/usr/bin/supervisord"]
