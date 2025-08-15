#FROM debian:latest
FROM nginx:1.22
RUN apt-get update && apt-get install -y init nano curl net-tools telnet 
RUN curl -O https://raw.githubusercontent.com/v2fly/fhs-install-v2ray/master/install-release.sh
RUN curl -O https://raw.githubusercontent.com/v2fly/fhs-install-v2ray/master/install-dat-release.sh
RUN bash install-release.sh
RUN bash install-dat-release.sh
RUN systemctl enable v2ray

COPY nginx.conf /etc/nginx/nginx.conf
COPY config2.json /usr/local/etc/v2ray/config.json
#COPY privateKey.key /etc/v2ray/v2ray.key
#COPY certificate.crt /etc/v2ray/v2ray.crt

CMD service nginx start && /usr/local/bin/v2ray run -config /usr/local/etc/v2ray/config.json
#CMD ["nginx", "-g", "daemon off;"]
# && /usr/local/bin/v2ray run -config /usr/local/etc/v2ray/config.json
