# AC MQTT proxy — dokumentáció / documentation

Broadlink Wi-Fi klímák (AUX, Dunham-Bush, TCL, Electrolux stb.) hídja a Home Assistant felé MQTT auto-discovery-vel.

---

## Elérhető funkciók

A kiegészítő minden beltérit **klíma (termosztát)** entitásként hoz létre, plusz külön vezérlőket.

### Klíma / termosztát (`climate.<név>`)

| Funkció | HA mező | Értékek |
|---|---|---|
| Üzemmód | `hvac_mode` | `off`, `cool`, `heat`, `dry`, `fan_only`, `auto` |
| Ventilátor | `fan_mode` | `Auto`, `Low`, `Medium`, `High`, `Turbo`, `Mute` |
| **Függőleges legyezés** | `swing_mode` | `TOP`, `MIDDLE1`, `MIDDLE2`, `MIDDLE3`, `BOTTOM`, `SWING`, `AUTO` |
| **Vízszintes legyezés** | `swing_horizontal_mode` | `LEFT_FIX`, `LEFT_FLAP`, `LEFT_RIGHT_FIX`, `LEFT_RIGHT_FLAP`, `RIGHT_FIX`, `RIGHT_FLAP` |
| Célhőmérséklet | `temperature` | 16–32 °C, 0,5 °C lépés |

A **vízszintes legyezés** a klíma more-info (részletek) ablakában jelenik meg. A dashboard **termosztátkártyán** külön feature kell:

```yaml
type: thermostat
entity: climate.acnappali_acnappali
features:
  - type: climate-hvac-modes
  - type: climate-fan-modes
    style: dropdown
  - type: climate-swing-modes
    style: dropdown
  - type: climate-swing-horizontal-modes
    style: dropdown
```

### Extra entitások (eszközoldal)

| Entitás | Funkció |
|---|---|
| `select.<név>_vertical_swing` | Függőleges lamella / legyezés |
| `select.<név>_horizontal_swing` | Vízszintes lamella / legyezés |
| `sensor.<név>_temp` | Beltéri hőmérséklet |
| `switch.<név>_display` | Kijelző LED |
| `switch.<név>_health` | Ionizátor / légtisztító |
| `switch.<név>_turbo` | Turbó |
| `switch.<név>_mute` | Csendes mód |
| `switch.<név>_sleep` | Alvás mód |
| `switch.<név>_clean` | Öntisztítás |

---

## Available functions

The add-on creates a **climate** entity per indoor unit, plus extra controls.

### Climate / thermostat (`climate.<name>`)

| Function | HA field | Values |
|---|---|---|
| Mode | `hvac_mode` | `off`, `cool`, `heat`, `dry`, `fan_only`, `auto` |
| Fan | `fan_mode` | `Auto`, `Low`, `Medium`, `High`, `Turbo`, `Mute` |
| **Vertical swing** | `swing_mode` | `TOP`, `MIDDLE1`, `MIDDLE2`, `MIDDLE3`, `BOTTOM`, `SWING`, `AUTO` |
| **Horizontal swing** | `swing_horizontal_mode` | `LEFT_FIX`, `LEFT_FLAP`, `LEFT_RIGHT_FIX`, `LEFT_RIGHT_FLAP`, `RIGHT_FIX`, `RIGHT_FLAP` |
| Target temperature | `temperature` | 16–32 °C, 0.5 °C step |

Horizontal swing appears in the climate more-info dialog. On a dashboard **thermostat card** add the feature `climate-swing-horizontal-modes` (see YAML above).

### Extra entities (device page)

| Entity | Function |
|---|---|
| `select.<name>_vertical_swing` | Vertical louver / swing |
| `select.<name>_horizontal_swing` | Horizontal louver / swing |
| `sensor.<name>_temp` | Indoor temperature |
| `switch.<name>_display` | Display LED |
| `switch.<name>_health` | Ionizer |
| `switch.<name>_turbo` | Turbo |
| `switch.<name>_mute` | Quiet mode |
| `switch.<name>_sleep` | Sleep |
| `switch.<name>_clean` | Self-clean |

---

## Konfiguráció / Configuration

- `mqtt.host` / `user` / `passwd`: hagyd üresen a belső Mosquittohoz.
- `devices`: klíma `ip`, `mac` (kisbetű, kettőspont nélkül), `name`, `port` (80).
- Opcionális külső hőmérő: `ext_temp_topic` / `ext_temp_template`, vagy a Blueprint.

Blueprint: [ac_external_temp_sync.yaml](https://github.com/klaigonzales/haos-broadlink-ac-mqtt/blob/master/blueprints/automation/klaigonzales/ac_external_temp_sync.yaml)
