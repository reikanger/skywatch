# official Python (Alpine Linux) runtime
FROM debian:stable-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install git, Python, pip, and supervisor
RUN apt-get update && \
    apt-get install -y git python3 python3-pip supervisor && \
    rm -rf /var/lib/apt/lists/*

# Clone the OpenSky API repository
RUN cd /app
RUN git clone https://github.com/openskynetwork/opensky-api.git

# Install the OpenSky API module
RUN pip3 install --break-system-packages -e ./opensky-api/python

# Install any needed packages specified in requirements.txt
RUN pip3 install --no-cache-dir --break-system-packages -r requirements.txt

# Make port 5000 (api) and port 8000 (web) available
EXPOSE 5000
EXPOSE 8000

COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Run supervisord when the container launches
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
