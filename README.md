# Home Assistant - AVS Alarm

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![maintainer](https://img.shields.io/badge/maintainer-%40lelenoce-blue.svg)](https://github.com/lelenoce)
[![license](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## Description
This Home Assistant component enables integration with the AVS alarm system. The component provides sensors and switches to monitor and control the alarm system directly from Home Assistant.

## Features
- Complete integration with AVS alarm system
- Sensors to monitor zone status
- Switches for system control
- Binary sensors for alarm events
- Local polling support
- Configurable through the Home Assistant UI
- Support for multiple zones
- Real-time status updates

## Requirements
- Home Assistant 2024.1.0 or newer
- Compatible AVS alarm system
- Access to the local network where the alarm system is installed
- Python 3.10 or newer

## Installation
### Method 1: HACS (Recommended)
1. Make sure you have [HACS](https://hacs.xyz/) installed
2. Click on HACS in the sidebar
3. Click on Integrations
4. Click the three dots in the top right
5. Click "Custom repositories"
6. Add `https://github.com/lelenoce/homeassistant-avs-alarm`
7. Select "Integration" as the category
8. Click "Add"
9. Search for "AVS Alarm"
10. Click "Download"
11. Restart Home Assistant
12. Add the integration through the UI

### Method 2: Manual Installation
1. Download the latest release
2. Copy the `avsalarm` folder to your Home Assistant `custom_components` directory
3. Restart Home Assistant
4. Add the "AVS Alarm" integration from the integrations page

## Configuration
The integration can be configured through the Home Assistant user interface:
1. Go to Settings > Devices & Services
2. Click on "Add Integration"
3. Search for "AVS Alarm"
4. Follow the on-screen instructions to complete the configuration

### Configuration Options
- **Host**: The IP address of your AVS alarm system
- **Port**: The port number (default: 80)
- **Username**: Your AVS system username
- **Password**: Your AVS system password
- **Scan Interval**: How often to poll the system for updates (default: 30 seconds)

## Components
- `sensor.py`: Manages system status sensors
- `binary_sensor.py`: Manages binary sensors for alarm events
- `switch.py`: Manages control switches
- `avs_api.py`: Implements communication with the AVS system

## Usage Examples
```yaml
# Example automation to notify when alarm is triggered
automation:
  - alias: "Alarm Triggered Notification"
    trigger:
      platform: state
      entity_id: binary_sensor.avsalarm_alarm_triggered
      to: "on"
    action:
      - service: notify.mobile_app
        data:
          message: "Alarm has been triggered!"

# Example automation to arm the system at night
automation:
  - alias: "Night Mode Alarm"
    trigger:
      platform: time
      at: "22:00:00"
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.avsalarm_arm_night
```

## Troubleshooting
If you encounter any issues:
1. Check that your AVS system is accessible on the network
2. Verify your credentials are correct
3. Check the Home Assistant logs for any error messages
4. Ensure your Home Assistant version is compatible

## Support
For support and bug reports:
- Open an issue on [GitHub](https://github.com/lelenoce/homeassistant-avs-alarm/issues)
- Join the [Home Assistant Community](https://community.home-assistant.io/)

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## License
This project is released under the MIT license. See the `LICENSE` file for more details.

## Authors
- [@lelenoce](https://github.com/lelenoce)

## Credits
- Thanks to all contributors and users of this integration
- Special thanks to the Home Assistant community for their support
