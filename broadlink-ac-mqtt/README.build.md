# Build hardening notes

This add-on downloads the upstream Broadlink AC MQTT package during the image build. To keep the build deterministic and reduce supply-chain drift, we pin the runtime package version and validate its checksum before extraction.

## Required follow-ups
- Keep the upstream archive URL version pinned.
- Verify SHA256 before extraction.
- Prefer maintained Python packages over deprecated crypto libraries where the runtime supports it.
- Validate MQTT and device configuration before the long-running loop starts.
- Add runtime monitoring for MQTT reconnects and per-device health.
