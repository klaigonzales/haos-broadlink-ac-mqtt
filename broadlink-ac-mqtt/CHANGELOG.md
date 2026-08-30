<!-- https://developers.home-assistant.io/docs/add-ons/presentation#keeping-a-changelog -->

## 0.9.2

- Fixed temperature jumping/flapping: separated internal AC ambient temperature topic (`/ambient_temp/value`) from climate current temperature (`/current_temp/value`) and added dedicated external temperature override receiver (`/ext_temp/set`)
- Updated Blueprint to publish to `/ext_temp/set` so external temperature overrides never conflict with internal hardware polling cycles

## 0.9.1

- Included direct Blueprint import URL in documentation and changelog:
  - Blueprint URL: `https://raw.githubusercontent.com/klaigonzales/haos-broadlink-ac-mqtt/master/blueprints/automation/klaigonzales/ac_external_temp_sync.yaml`
  - 1-Click Import link: `https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fraw.githubusercontent.com%2Fklaigonzales%2Fhaos-broadlink-ac-mqtt%2Fmaster%2Fblueprints%2Fautomation%2Fklaigonzales%2Fac_external_temp_sync.yaml`

## 0.9.0

- Added external temperature sensor binding support directly in add-on configuration (`ext_temp_topic` and `ext_temp_template`)
- Created official Home Assistant Automation Blueprint (`ac_external_temp_sync.yaml`) to bind any Home Assistant temperature entity to the AC with zero YAML editing
  - Blueprint: `https://github.com/klaigonzales/haos-broadlink-ac-mqtt/blob/master/blueprints/automation/klaigonzales/ac_external_temp_sync.yaml`
- Subscribed to custom external temperature topics automatically upon MQTT connect

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