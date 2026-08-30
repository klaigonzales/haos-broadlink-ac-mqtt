ARG BUILD_FROM
FROM $BUILD_FROM

COPY rootfs /

RUN apk add --no-cache gcc g++ make \
    && pip3 install --no-cache-dir -U \
        paho-mqtt==1.6.1 \
        pyyaml==6.0.2 \
        pycryptodome==3.20.0 \
    && cd /usr/share \
    && wget -O broadlink-ac-mqtt.tar.gz "https://github.com/liaan/broadlink_ac_mqtt/archive/refs/tags/1.2.1b.tar.gz" \
    && echo "7f0a2e4807f6d50f4b6fd6fc2e5b86426cb34db33a16d88b4d7402d6fb09e6d6  broadlink-ac-mqtt.tar.gz" | sha256sum -c - \
    && tar -xzf broadlink-ac-mqtt.tar.gz \
    && rm -f broadlink-ac-mqtt.tar.gz \
    && chmod a+x /etc/services.d/broadlink-ac-mqtt/*
