FROM alpine:latest
LABEL maintainer="Your Name <your_email@example.com>"
RUN apk add --no-cache curl
RUN curl -L -H "Cache-Control: no-cache" -o /v2ray.zip https://github.com/v2fly/v2ray-core/releases/download/v4.53.1/v2ray-linux-64.zip && \
    mkdir /usr/bin/v2ray && \
    unzip /v2ray.zip -d /usr/bin/v2ray/ && \
    rm /v2ray.zip
COPY config.json /etc/v2ray/config.json
EXPOSE 80
CMD ["/usr/bin/v2ray/v2ray", "-config=/etc/v2ray/config.json"]
