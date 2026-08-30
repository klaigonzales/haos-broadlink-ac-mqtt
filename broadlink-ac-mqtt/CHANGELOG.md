<!-- https://developers.home-assistant.io/docs/add-ons/presentation#keeping-a-changelog -->

## 0.7.1

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