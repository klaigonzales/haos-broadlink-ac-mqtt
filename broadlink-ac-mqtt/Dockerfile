ARG BUILD_FROM
FROM $BUILD_FROM

## Upstream 1.2.4 plus the unmapped-fan-speed fix, pinned by commit rather than
## by tag: a tag can be moved, and then the same add-on version would build
## different code with nothing in this repository to show for it. Bump together
## with config.yaml's version.
ARG UPSTREAM_COMMIT=b86c16b5c17b5a8a3350684e9f1efeec892ef3f8

COPY rootfs /

## Install runtime dependencies using prebuilt wheels from Home Assistant index.
RUN mkdir -p /usr/share/broadlink_ac_mqtt \
    && wget -qO- "https://github.com/Arbuzov/broadlink_ac_mqtt/archive/${UPSTREAM_COMMIT}.tar.gz" \
       | tar -xz -C /usr/share/broadlink_ac_mqtt --strip-components=1 \
    && pip3 install --no-cache-dir -r /usr/share/broadlink_ac_mqtt/requirements.txt "cryptography<50" \
    && chmod a+x /etc/services.d/broadlink-ac-mqtt/*