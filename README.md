# Home Assistant Add-on: AC MQTT Proxy

Home Assistant OS (HAOS) kiegészítő (Add-on) Broadlink Wi-Fi modullal szerelt klímaberendezésekhez (pl. Aux, DunAn, TCL, stb.) MQTT protokollon keresztül.

---

## 🚀 Telepítés Home Assistant alatt

1. **Egyéni kiegészítő tároló hozzáadása:**
   - Nyisd meg a Home Assistantot.
   - Lépj ide: **Beállítások (Settings) -> Bővítmények (Add-ons) -> Kiegészítő-áruház (Add-on Store)**.
   - Kattints a jobb felső három pontra (⋮), majd válaszd a **Tárolók (Repositories)** menüpontot.
   - Add hozzá az alábbi URL-t:
     ```
     https://github.com/klaigonzales/haos-broadlink-ac-mqtt
     ```
   - Kattints a **Hozzáadás (Add)** gombra, majd zárd be az ablakot.

2. **Kiegészítő telepítése:**
   - Frissítsd az áruház oldalát.
   - Keresd meg az **AC MQTT proxy for home assistant** kiegészítőt és kattints a **Telepítés (Install)** gombra.

3. **MQTT Broker beállítása:**
   - Győződj meg róla, hogy a Mosquitto broker telepítve van és fut a Home Assistantban.

4. **Konfiguráció:**
   - A kiegészítő **Konfiguráció (Configuration)** fülén állítsd be az MQTT kapcsolatot és add hozzá a klímáid IP/MAC címeit.
