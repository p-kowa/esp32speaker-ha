# ESP32 Speaker

Home Assistant custom integration that adds one media player to an ESP32 Speaker
already discovered by the MQTT integration. Existing switches, sensors, selects,
volume controls and alarm entities remain unchanged. No second physical device is
created, and MQTT retains ownership of the device.

Firmware: [p-kowa/esp32speaker, with_wakeword_i18n](https://github.com/p-kowa/esp32speaker/tree/with_wakeword_i18n).

## Requirements

- Home Assistant 2026.10 or newer, as required by this project's blueprint.
- The MQTT integration connected to the same broker as the speaker.
- Enabled MQTT radio power and volume entities for the speaker.
- The firmware device ID returned by `GET http://<speaker-ip>/api/device/id`.

Docker is not required for installation or use. This helper does not poll HTTP;
copy the device ID from the endpoint once during setup.

## Installation

1. Copy `custom_components/esp32speaker_integration` from this repository into
   `<home-assistant-config>/custom_components/esp32speaker_integration`.
2. Restart Home Assistant.
3. Under **Settings > Devices & services > Helpers**, choose **Create helper** and
   find **ESP32 Speaker**. The helper may also be accessible through the integration
   setup picker, depending on the Home Assistant frontend version.
4. Enter the firmware device ID, select the existing MQTT radio power switch and
   enter the MQTT base topic configured on the speaker.

Example for the speaker discussed in this project:

| Setting | Value |
| --- | --- |
| Firmware device ID | `F88B419FC114` |
| Radio power switch | `switch.esp32_radio_esp32radio_419fc114_radio_power` |
| MQTT topic prefix | `esp32radio-419FC114` |

Do not use Home Assistant's internal device registry ID, such as
`002dc75ef216af1bd4439d57e9f43db8`, as the firmware ID. Do not append `/set` or
`/state` to the topic prefix.

The helper checks the submitted values against the firmware's MQTT discovery
unique IDs. It finds volume, title, station, radio favorites, SD selection and
announcement status from the same MQTT device. Entity names and translations do
not need to match the examples above. Optional entities absent during setup are
not required; reconfigure the helper after enabling them or renaming source entities.

Repeat setup for each physical speaker, using its own ID, power switch and prefix.
Changing the prefix requires the firmware to publish fresh MQTT discovery first;
then use **Reconfigure** on the helper to refresh the mapping.

## Supported Controls

- Start the last or first stored radio station, or stop playback.
- Set volume and step it up/down; firmware levels `0..21` map to `0..1` in HA.
- Display the live playback state, current station and title.
- Select favorites as `Radio: <name>` and SD files as `SD: <path>`.
- Play HTTP(S) audio URLs and Home Assistant media sources, including TTS.
- Play announcements with firmware-managed restoration of the previous playback.

Example action (replace the entity ID with the new media player):

```yaml
action: media_player.play_media
target:
  entity_id: media_player.esp32_radio
data:
  media_content_id: "http://your-audio-server/example.mp3"
  media_content_type: music
  announce: true
```

Normal URLs are published to `<base>/set/station_url`, announcements to
`<base>/set/announce`, always with `retain: false`. Home Assistant resolves media
source references to an audio URL; that URL must be reachable by the ESP32.
SD paths listed by the existing SD select can also be passed as `media_content_id`.

## Limitations

- No real pause/resume, seek, track position, mute or queue support is advertised.
- Start means radio startup, not resuming a stopped SD file at its previous position.
- The power switch reports playback, so stopped playback is `idle`, not `off`.
- Unknown source state remains unknown; a missing/offline power entity makes the
  media player unavailable. No optimistic state is written after commands.
- The firmware sends status periodically, so command confirmation may take a few seconds.
- Wake word, speech recognition and Assist satellite support are not implemented here.
- Old blueprint demo entries cannot be migrated into physical speakers; remove any
  installed demo entry and configure the helper afresh.

## Verification

Tests cover setup validation, duplicate prevention, renamed source entities,
reconfiguration, media controls, state propagation, MQTT commands, unload and
device ownership. Run them in a compatible Python 3.14 development environment:

```bash
script/test tests/test_entities.py tests/test_config_flow.py tests/test_blueprint_device_registry.py
script/lint
script/type-check
script/hassfest
```

Current implementation status: AI-assisted and not yet human-reviewed or tested
on a real Home Assistant instance or speaker. The automated suite could not be
run in the current Windows workspace because the project virtual environment is
missing and only Python 3.11 is registered. Do not treat the tests as passing.

## License

MIT. See [LICENSE](LICENSE).