ARG BUILD_FROM
FROM $BUILD_FROM

ARG UPSTREAM_COMMIT=b86c16b5c17b5a8a3350684e9f1efeec892ef3f8

## Install runtime dependencies using prebuilt wheels from Home Assistant index.
RUN mkdir -p /usr/share/broadlink_ac_mqtt \
    && wget -qO- "https://github.com/Arbuzov/broadlink_ac_mqtt/archive/${UPSTREAM_COMMIT}.tar.gz" \
       | tar -xz -C /usr/share/broadlink_ac_mqtt --strip-components=1 \
    && pip3 install --no-cache-dir -r /usr/share/broadlink_ac_mqtt/requirements.txt "cryptography<50"

## Copy rootfs overlay (includes service supervisor scripts and enhanced custom modules)
COPY rootfs /

RUN chmod a+x /etc/services.d/broadlink-ac-mqtt/*