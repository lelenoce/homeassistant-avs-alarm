from homeassistant.components.switch import SwitchEntity
import logging
import requests

_LOGGER = logging.getLogger(__name__)

class AVSAlarmZoneSwitch(SwitchEntity):
    """Representation of a switch for an AVS Alarm zone."""

    def __init__(self, hass, name, ip, port, user, pid, zone):
        self._hass = hass
        self._name = name
        self._ip = ip
        self._port = port
        self._user = user
        self._pid = pid
        self._zone = zone
        self._state = False

    @property
    def name(self):
        return self._name

    @property
    def is_on(self):
        return self._state

    async def async_turn_on(self):
        url = f"http://{self._ip}:{self._port}/cmd/zone/alarm?ultra=kOU9Rc885y1Gia3p&pid={self._pid}&user={self._user}&zone={self._zone}"
        try:
            response = await self._hass.async_add_executor_job(requests.get, url)
            if response.status_code == 200:
                self._state = True
            else:
                _LOGGER.error(f"Errore durante l'invio del comando turn on: {response.status_code}")
        except Exception as e:
            _LOGGER.error(f"Errore nell'invio del comando: {e}")

    async def async_turn_off(self):
        await self.async_disarm()

    async def async_disarm(self):
        url = f"http://{self._ip}:{self._port}/cmd/zone/restore?ultra=kOU9Rc885y1Gia3p&pid={self._pid}&user={self._user}&zone={self._zone}"
        try:
            response = await self._hass.async_add_executor_job(requests.get, url)
            if response.status_code == 200:
                self._state = False
            else:
                _LOGGER.error(f"Errore durante l'invio del comando disarm: {response.status_code}")
        except Exception as e:
            _LOGGER.error(f"Errore nell'invio del comando disarm: {e}")


def setup_zones(hass, ip, port, user, pid):
    """Setup zone switches."""
    return [AVSAlarmZoneSwitch(hass, "AVS Alarm Zone 30", ip, port, user, pid, 30)]