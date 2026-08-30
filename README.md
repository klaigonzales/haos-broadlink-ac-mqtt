# Home Assistant Add-on: AC MQTT Proxy

[![GitHub Release](https://img.shields.io/github/v/release/klaigonzales/haos-broadlink-ac-mqtt?color=blue)](https://github.com/klaigonzales/haos-broadlink-ac-mqtt/releases)
[![License](https://img.shields.io/github/license/klaigonzales/haos-broadlink-ac-mqtt)](https://github.com/klaigonzales/haos-broadlink-ac-mqtt/blob/master/LICENSE)

A powerful Home Assistant OS (HAOS) Add-on to bridge **Broadlink-based Wi-Fi Air Conditioners** (AUX, Dunham-Bush, TCL, Electrolux, etc.) with Home Assistant via MQTT with full auto-discovery and external temperature sensor binding support.

*Home Assistant OS kiegészítő Broadlink Wi-Fi modullal szerelt klímaberendezésekhez (AUX, Dunham-Bush, TCL, Electrolux stb.) MQTT protokollon, automatikus felderítésen és külső hőmérséklet-érzékelő támogatással.*

---

## 🌐 Language / Nyelv
- [English](#-english)
- [Magyar](#-magyar)
- [🌡️ External Temperature Binding / Külső hőmérő hozzárendelése](#-external-temperature-sensor-binding--k%C3%BCls%C5%91-h%C5%91m%C3%A9rs%C3%A9klet-%C3%A9rz%C3%A9kel%C5%91-hozz%C3%A1rendel%C3%A9se)

---

## 🇬🇧 English

### ✨ Features
- **Seamless MQTT Discovery:** Automatically creates Climate entities and exposes extra device controls without manual YAML configuration.
- **External Temperature Sensor Binding:** Bind any external temperature sensor (Zigbee, Shelly, BLE, ESPHome, etc.) directly in add-on options or using our official Automation Blueprint.
- **Dedicated Device Entities:**
  - **Thermostat / Climate:** Modes (`auto`, `cool`, `heat`, `dry`, `fan_only`, `off`), fan speeds (`auto`, `low`, `medium`, `high`, `turbo`, `mute`), vertical swing, temperature setpoint (`16°C – 32°C`).
  - **Ambient Temperature Sensor (`sensor.<ac>_temp`):** Room temperature with `measurement` state class for long-term statistics & graphs.
  - **Display Switch (`switch.<ac>_display`):** Turn indoor unit LED panel on/off.
  - **Health / Plasma Switch (`switch.<ac>_health`):** Control ionizer / air purification.
  - **Turbo Switch (`switch.<ac>_turbo`):** One-touch maximum cooling/heating.
  - **Mute Switch (`switch.<ac>_mute`):** Ultra-quiet mode.
  - **Sleep Switch (`switch.<ac>_sleep`):** Night sleep mode.
  - **Clean Switch (`switch.<ac>_clean`):** Self-cleaning cycle.
- **Per-Device Availability:** Offline status tracking per device (`<prefix>/<mac>/availability`) with debouncing.
- **Internal Mosquitto Auto-Discovery:** Leaves broker credentials empty to automatically use Home Assistant's internal Mosquitto add-on.
- **Offline / IoT VLAN Fallback:** Robust local IP resolution without external DNS dependencies.
- **Supported Hardware:** `0x4E2a`, `0x4E2b`, `0x4E2c`, `0x4E2d`, `0x4E4d`, `0x4F05` (and entire `0x4E00` series).

### 🚀 Installation in Home Assistant

1. **Add Custom Repository:**
   - Go to **Settings -> Add-ons -> Add-on Store**.
   - Click the top-right menu (⋮) -> **Repositories**.
   - Add the repository URL:
     ```
     https://github.com/klaigonzales/haos-broadlink-ac-mqtt
     ```
   - Click **Add** and close the dialog.

2. **Install the Add-on:**
   - Refresh the page and find **AC MQTT proxy for home assistant**.
   - Click **Install**.

3. **Configure:**
   - Navigate to the **Configuration** tab.
   - If using the official Mosquitto broker, leave `mqtt.host`, `user`, and `passwd` empty (auto-configured).
   - Enter your AC units under `devices` with their local **IP** and **MAC** addresses (lowercase hex without colons).
   - Click **Save** and **Start**.

---

## 🇭🇺 Magyar

### ✨ Funkciók
- **Automatikus Home Assistant MQTT felismerés (Auto-Discovery):** Kézi YAML konfiguráció nélkül hozza létre a klímát és a kapcsolódó vezérlőket.
- **Külső hőmérséklet-érzékelő hozzárendelése:** Bármilyen szobai/külső hőmérő (Zigbee, Shelly, ESPHome stb.) hozzárendelhető a klíma kártyájához a konfigurációban vagy az automatizálási sablonnal.
- **Dedikált eszközvezérlők:**
  - **Klíma / Termosztát:** Módok (`auto`, `cool`, `heat`, `dry`, `fan_only`, `off`), ventilátorfokozatok (`auto`, `low`, `medium`, `high`, `turbo`, `mute`), lamellamozgatás, hőmérséklet állítás (`16°C – 32°C`).
  - **Helyiség Hőmérséklet Érzékelő (`sensor.<klima>_temp`):** Különálló szenzor grafikonokhoz és hosszú távú statisztikákhoz.
  - **Kijelző Kapcsoló (`switch.<klima>_display`):** Beltéri LED kijelző le-/felkapcsolása (pl. éjszakai automatizációhoz).
  - **Egészség / Plazma Kapcsoló (`switch.<klima>_health`):** Beépített ionizátor / légtisztító vezérlése.
  - **Turbó Kapcsoló (`switch.<klima>_turbo`):** Gyors maximális hűtés/fűtés.
  - **Csendes Kapcsoló (`switch.<klima>_mute`):** Csendes éjszakai üzemmód.
  - **Alvás Mód (`switch.<klima>_sleep`):** Éjszakai intelligens hőmérsékletszabályzás.
  - **Öntisztítás (`switch.<klima>_clean`):** Beltéri egység szárító/tisztító ciklusa.
- **Eszközönkénti elérhetőség (Per-device Availability):** Intelligens szűréssel (debounce), nem ugrál a kapcsolat csomagvesztéskor.
- **Mosquitto automatikus integráció:** Üresen hagyott MQTT beállítások esetén automatikusan átveszi a belső Mosquitto broker hitelesítését.
- **Offline / Elzárt VLAN támogatás:** Nem igényel külső internetkapcsolatot vagy DNS elérést.

---

## 🌡️ External Temperature Sensor Binding / Külső hőmérséklet-érzékelő hozzárendelése

A klímához **kétféleképpen** rendelhetsz hozzá külső hőmérséklet-érzékelőt:

### Opció A: Automatizálási Sablonnal (Blueprint) — *Bármilyen Home Assistant szenzorhoz*
Ha az érzékelőd Zigbee, Bluetooth, Shelly, ESPHome vagy virtuális szenzor:
1. Nyisd meg a Home Assistantban a **Beállítások -> Automatizmusok és jelenetek -> Sablonok (Blueprints)** menüt.
2. Kattints a **Sablon importálása** gombra a jobb alsó sarokban.
3. Másold be ezt az URL-t:
   ```
   https://github.com/klaigonzales/haos-broadlink-ac-mqtt/blob/master/blueprints/automation/klaigonzales/ac_external_temp_sync.yaml
   ```
4. Kattints az **Automatizmus létrehozása** gombra, majd a grafikus felületen:
   - Válaszd ki a külső hőmérődet a legördülő listából.
   - Írd be a klímád MAC-címét (pl. `34ea34xxxxxx`).
   - Kattints a **Mentés** gombra!

### Opció B: Közvetlen Add-on konfigurációban — *Ha a külső érzékelő MQTT-n küld adatot*
Ha a külső hőmérőd MQTT-n keresztül kommunikál (pl. Zigbee2MQTT, Tasmota stb.):
Az Add-on **Konfiguráció** lapján a klímád alatt add meg az `ext_temp_topic` mezőt:
```yaml
devices:
  - ip: 192.168.1.50
    mac: 34ea34a1b2c3
    name: Living Room AC
    port: 80
    ext_temp_topic: "zigbee2mqtt/living_room_temp_sensor/temperature"
```
