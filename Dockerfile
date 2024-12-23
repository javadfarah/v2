# Start from the Nginx image
FROM nginx:1.22

# Install necessary tools and Python
RUN apt-get update && \
    apt-get install -y init nano curl procps net-tools telnet python3 python3-pip && \
    curl -O https://raw.githubusercontent.com/v2fly/fhs-install-v2ray/master/install-release.sh && \
    curl -O https://raw.githubusercontent.com/v2fly/fhs-install-v2ray/master/install-dat-release.sh && \
    bash install-release.sh && \
    bash install-dat-release.sh && \
    systemctl enable v2ray

# Copy configuration files for Nginx and V2Ray
COPY nginx.conf /etc/nginx/nginx.conf
COPY config.json /usr/local/etc/v2ray/config.json

# Install Python dependencies
COPY requirements.txt /tmp/requirements.txt
RUN pip3 --timeout=1000 install --no-cache-dir -r /tmp/requirements.txt

# Copy Python application code
COPY . /app

# Set the working directory to the Python app directory
WORKDIR /app

# Expose ports (you can adjust these if needed)
EXPOSE 80 443 8080

# Start Nginx and V2Ray services, then run the Python application
CMD service nginx start & /usr/local/bin/v2ray run -config /usr/local/etc/v2ray/config.json & python3 /app/main.py
