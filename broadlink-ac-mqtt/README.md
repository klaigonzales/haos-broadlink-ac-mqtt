# Home Assistant Add-on: AC MQTT Proxy

Bridge between Broadlink-based Wi-Fi Air Conditioners (AUX, Dunham-Bush, TCL, etc.) and Home Assistant via MQTT with full auto-discovery support.

---

## Features

- **Climate Entity:** Modes (`auto`, `cool`, `heat`, `dry`, `fan_only`, `off`), fan speeds (`auto`, `low`, `medium`, `high`, `turbo`, `mute`), vertical swing, target temperature (`16°C – 32°C`, step: 0.5).
- **Extra Entities:** Ambient temperature sensor, display light switch, health/ionizer switch, turbo, mute, sleep, and self-clean switches.
- **Per-Device Availability:** Offline status tracked per unit (`<topic_prefix>/<mac>/availability`).
- **Automatic Mosquitto Integration:** Automatically fetches credentials from the Home Assistant Supervisor when `mqtt.host` is empty.
- **Network Resilience:** Safe local IP discovery with offline/VLAN fallback.

---

## Configuration

```yaml
service:
  daemon_mode: true
  update_interval: 10
  self_discovery: false
  bind_to_ip: false
  debug: false
  log_level: INFO
  log_level_console: INFO
mqtt:
  host: ""
  port: 1883
  client_id: ac_to_mqtt
  user: ""
  passwd: ""
  topic_prefix: /aircon
  auto_discovery_topic: homeassistant
  auto_discovery_topic_retain: false
  discovery: false
devices:
  - ip: 192.168.1.50
    mac: 34ea34a1b2c3
    name: Living Room AC
    port: 80
```

### Configuration Options

| Option | Type | Description |
| :--- | :--- | :--- |
| `service.daemon_mode` | boolean | Keeps the add-on running continuously. |
| `service.update_interval` | integer | Polling interval in seconds (default: 10). |
| `service.self_discovery` | boolean | Automatically discovers AC units on the local subnet via UDP broadcast. |
| `service.bind_to_ip` | boolean/string | Bind to specific network interface IP (`false` for auto). |
| `service.debug` | boolean | Enables verbose debug logging in Home Assistant logs. |
| `service.log_level_console` | string | Log level for the Home Assistant add-on log (`DEBUG`, `INFO`, `WARNING`, `ERROR`). |
| `mqtt.host` | string | MQTT broker address (leave empty for internal Mosquitto). |
| `mqtt.port` | integer | MQTT broker port (default: 1883). |
| `mqtt.topic_prefix` | string | MQTT root topic prefix (default: `/aircon`). |
| `mqtt.auto_discovery_topic` | string | Home Assistant MQTT discovery prefix (default: `homeassistant`). |
| `devices` | list | List of AC devices with `ip`, `mac`, `name`, and `port`. |
