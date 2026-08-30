# Home Assistant Add-on: AC MQTT Proxy

[![GitHub Release](https://img.shields.io/github/v/release/klaigonzales/haos-broadlink-ac-mqtt?color=blue)](https://github.com/klaigonzales/haos-broadlink-ac-mqtt/releases)
[![License](https://img.shields.io/github/license/klaigonzales/haos-broadlink-ac-mqtt)](https://github.com/klaigonzales/haos-broadlink-ac-mqtt/blob/master/LICENSE)

A powerful Home Assistant OS (HAOS) Add-on to bridge **Broadlink-based Wi-Fi Air Conditioners** (AUX, Dunham-Bush, TCL, Electrolux, etc.) with Home Assistant via MQTT with full auto-discovery support.

*Home Assistant OS kiegészítő Broadlink Wi-Fi modullal szerelt klímaberendezésekhez (AUX, Dunham-Bush, TCL, Electrolux stb.) MQTT protokollon és automatikus felderítésen keresztül.*

---

## 🌐 Language / Nyelv
- [English](#-english)
- [Magyar](#-magyar)

---

## 🇬🇧 English

### ✨ Features
- **Seamless MQTT Discovery:** Automatically creates Climate entities and exposes extra device controls without manual YAML configuration.
- **Dedicated Device Entities:**
  - **Thermostat / Climate:** Modes (`auto`, `cool`, `heat`, `dry`, `fan_only`, `off`), fan speeds (`auto`, `low`, `medium`, `high`, `turbo`, `mute`), vertical swing, temperature setpoint (`16°C – 32°C`).
  - **Ambient Temperature Sensor (`sensor.<ac>_temp`):** Room temperature with `measurement` state class for long-term statistics & graphs.
  - **Display Switch (`switch.<ac>_display`):** Turn indoor unit LED panel on/off.
  - **Health / Plasma Switch (`switch.<ac>_health`):** Control ionizer / air purification.
  - **Turbo Switch (`switch.<ac>_turbo`):** One-touch maximum cooling/heating.
  - **Mute Switch (`switch.<ac>_mute`):** Ultra-quiet mode.
  - **Sleep Switch (`switch.<ac>_sleep`):** Night sleep mode.
  - **Clean Switch (`switch.<ac>_clean`):** Self-cleaning cycle.
- **Per-Device Availability:** Offline status tracking per device (`<prefix>/<mac>/availability`).
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
- **Dedikált eszközvezérlők:**
  - **Klíma / Termosztát:** Módok (`auto`, `cool`, `heat`, `dry`, `fan_only`, `off`), ventilátorfokozatok (`auto`, `low`, `medium`, `high`, `turbo`, `mute`), lamellamozgatás, hőmérséklet állítás (`16°C – 32°C`).
  - **Helyiség Hőmérséklet Érzékelő (`sensor.<klima>_temp`):** Különálló szenzor grafikonokhoz és hosszú távú statisztikákhoz.
  - **Kijelző Kapcsoló (`switch.<klima>_display`):** Beltéri LED kijelző le-/felkapcsolása (pl. éjszakai automatizációhoz).
  - **Egészség / Plazma Kapcsoló (`switch.<klima>_health`):** Beépített ionizátor / légtisztító vezérlése.
  - **Turbó Kapcsoló (`switch.<klima>_turbo`):** Gyors maximális hűtés/fűtés.
  - **Csendes Kapcsoló (`switch.<klima>_mute`):** Csendes éjszakai üzemmód.
  - **Alvás Mód (`switch.<klima>_sleep`):** Éjszakai intelligens hőmérsékletszabályzás.
  - **Öntisztítás (`switch.<klima>_clean`):** Beltéri egység szárító/tisztító ciklusa.
- **Eszközönkénti elérhetőség (Per-device Availability):** Ha egy klíma lekapcsol, csak az adott eszköz válik offline állapotúvá.
- **Mosquitto automatikus integráció:** Üresen hagyott MQTT beállítások esetén automatikusan átveszi a belső Mosquitto broker hitelesítését.
- **Offline / Elzárt VLAN támogatás:** Nem igényel külső internetkapcsolatot vagy DNS elérést.

### 🚀 Telepítés Home Assistant alatt

1. **Egyéni tároló hozzáadása:**
   - Nyisd meg a Home Assistantot: **Beállítások -> Bővítmények -> Kiegészítő-áruház**.
   - Kattints a jobb felső sarokban a menüre (⋮) -> **Tárolók (Repositories)**.
   - Add hozzá az alábbi URL-t:
     ```
     https://github.com/klaigonzales/haos-broadlink-ac-mqtt
     ```
   - Kattints a **Hozzáadás** gombra.

2. **Kiegészítő telepítése:**
   - Frissítsd az áruházat, keresd meg az **AC MQTT proxy for home assistant** kiegészítőt, majd kattints a **Telepítés** gombra.

3. **Konfiguráció:**
   - Nyisd meg a kiegészítő **Konfiguráció** fülét.
   - Ha a hivatalos Mosquitto add-ont használod, az `mqtt.host`, `user` és `passwd` mezőket hagyd üresen.
   - Add meg a klímáid **IP** és **MAC** címét (kettőspontok nélkül, kisbetűkkel).
   - Kattints a **Mentés** gombra, majd indítsd el a kiegészítőt.

---

## ⚙️ Configuration Example / Példa konfiguráció

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
