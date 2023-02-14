FROM alpine:latest

ARG V2RAY_VERSION=5.3.0

RUN apk --no-cache add wget tar \
 && wget https://github.com/v2fly/v2ray-core/releases/download/v${V2RAY_VERSION}/v2ray-linux-64.zip \
 && unzip v2ray-linux-64.zip \
 && rm v2ray-linux-64.zip \
 && mkdir -p /usr/bin/v2ray /etc/v2ray \
 && mv v2ray v2ctl geoip.dat geosite.dat /usr/bin/v2ray \
 && chmod +x /usr/bin/v2ray/v2ray /usr/bin/v2ray/v2ctl \
 && wget https://raw.githubusercontent.com/v2fly/domain-list-community/release/dlc.dat -O /usr/bin/v2ray/dlc.dat \
 && wget https://raw.githubusercontent.com/v2fly/domain-list-community/release/geosite.dat -O /usr/bin/v2ray/geosite.dat

COPY config.json /etc/v2ray/config.json

EXPOSE 80

CMD ["/usr/bin/v2ray/v2ray", "-config=/etc/v2ray/config.json"]
