# Home Assistant - AVS Alarm

## Description
This Home Assistant component enables integration with the AVS alarm system. The component provides sensors and switches to monitor and control the alarm system directly from Home Assistant.

## Features
- Complete integration with AVS alarm system
- Sensors to monitor zone status
- Switches for system control
- Binary sensors for alarm events
- Local polling support

## Requirements
- Home Assistant installed and configured
- Compatible AVS alarm system
- Access to the local network where the alarm system is installed

## Installation
1. Copy the `avsalarm` folder to your Home Assistant `custom_components` directory
2. Restart Home Assistant
3. Add the "AVS Alarm" integration from the integrations page

## Configuration
The integration can be configured through the Home Assistant user interface:
1. Go to Settings > Devices & Services
2. Click on "Add Integration"
3. Search for "AVS Alarm"
4. Follow the on-screen instructions to complete the configuration

## Components
- `sensor.py`: Manages system status sensors
- `binary_sensor.py`: Manages binary sensors for alarm events
- `switch.py`: Manages control switches
- `avs_api.py`: Implements communication with the AVS system

## Support
For support and bug reports, please open an issue on GitHub.

## License
This project is released under the MIT license. See the `LICENSE` file for more details.

## Authors
- @lelenoce
