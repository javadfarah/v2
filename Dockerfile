#FROM debian:latest
# FROM nginx:1.22
# RUN apt-get update && apt-get install -y init nano curl net-tools telnet 
# RUN curl -O https://raw.githubusercontent.com/v2fly/fhs-install-v2ray/master/install-release.sh
# RUN curl -O https://raw.githubusercontent.com/v2fly/fhs-install-v2ray/master/install-dat-release.sh
# RUN bash install-release.sh
# RUN bash install-dat-release.sh
# RUN systemctl enable v2ray

# COPY nginx.conf /etc/nginx/nginx.conf
# COPY config.json /usr/local/etc/v2ray/config.json
#COPY privateKey.key /etc/v2ray/v2ray.key
#COPY certificate.crt /etc/v2ray/v2ray.crt

# CMD service nginx start && /usr/local/bin/v2ray run -config /usr/local/etc/v2ray/config.json
#CMD ["nginx", "-g", "daemon off;"]
# && /usr/local/bin/v2ray run -config /usr/local/etc/v2ray/config.json
FROM nginx:1.22

RUN apt-get update && \
    apt-get install -y curl unzip

RUN curl -L https://github.com/XTLS/Xray-core/releases/latest/download/Xray-linux-64.zip \
    -o xray.zip && \
    unzip xray.zip && \
    mv xray /usr/local/bin/xray && \
    chmod +x /usr/local/bin/xray
RUN mkdir -p /var/log/v2ray
COPY config.json /usr/local/etc/xray/config.json
COPY nginx.conf /etc/nginx/nginx.conf

CMD service nginx start && \
    /usr/local/bin/xray run -config /usr/local/etc/xray/config.json
