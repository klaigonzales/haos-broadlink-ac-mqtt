# Home Assistant Add-on: AC MQTT proxy for home assistant

Bridge between Broadlink-based Wi-Fi Air Conditioners and Home Assistant via MQTT.

## Configuration

```yaml
service:
  daemon_mode: true
  update_interval: 10
  self_discovery: false
  bind_to_ip: false
mqtt:
  host: core-mosquitto
  port: 1883
  client_id: ac_to_mqtt
  user: mqtt_user
  passwd: mqtt_password
  topic_prefix: /aircon
  auto_discovery_topic: homeassistant
  auto_discovery_topic_retain: false
  discovery: false
devices:
  - ip: 192.168.1.50
    mac: 34ea34xxxxxx
    name: Living Room AC
    port: 80
```
