<!-- https://developers.home-assistant.io/docs/add-ons/presentation#keeping-a-changelog -->

## 0.8.1

- Debounced per-device availability tracking (requires 3 consecutive dropped poll cycles before marking unavailable) to eliminate status flapping on Wi-Fi packet drops

- Added automatic Home Assistant MQTT Discovery for extra entities:
  - Separate Ambient Temperature Sensor (`sensor.<ac>_temp`)
  - Display LED Light Switch (`switch.<ac>_display`)
  - Health / Plasma Ionizer Switch (`switch.<ac>_health`)
  - Turbo Mode Switch (`switch.<ac>_turbo`)
  - Mute / Quiet Mode Switch (`switch.<ac>_mute`)
  - Sleep Mode Switch (`switch.<ac>_sleep`)
  - Clean / Self-Clean Switch (`switch.<ac>_clean`)
- Added per-device MQTT Availability tracking (`<prefix>/<mac>/availability`)
- Expanded Broadlink AC hardware devtype support (`0x4E2a`, `0x4E2b`, `0x4E2c`, `0x4E2d`, `0x4E4d`, `0x4F05`)
- Full Hungarian and English UI translations (`translations/hu.yaml`, `translations/en.yaml`)
- Added `panel_icon` and `stage: stable` metadata

- Enhanced Home Assistant Device Registry integration with structured device metadata
- Added explicit climate modes (`auto`, `cool`, `heat`, `dry`, `fan_only`, `off`) and temp limits
- Robust DNS / local IP resolution fallback for isolated and IoT VLAN networks
- Updated GitHub Actions CI linting workflows

- Switched to maintained upstream `Arbuzov/broadlink_ac_mqtt`
- Base Python image updated to Python 3.13 / Alpine 3.22
- Migrated cryptography dependency to modern `cryptography<50`
- Integrated Supervisor MQTT auto-discovery (`services: - mqtt:want`)
- Added `service.debug`, `service.log_level`, `service.log_level_console` configuration support
- Fixed device timeouts, reconnect recovery loop, and unmapped fan speed handling

## 0.6.3

- Cosmetic changes at readme
- CHANGELOG added to the project
- vscode tools added to simplify the development

## 0.6.2

- Initial release