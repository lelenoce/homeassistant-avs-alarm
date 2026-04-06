import requests
import logging
from typing import Any
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

def open_session(ip, port, user, pid):
    """
    Apri una sessione con il sistema AVS.
    """
    session_url = f"http://{ip}:{port}/session/open?ultra=kOU9Rc885y1Gia3p&pid={pid}&user={user}"
    try:
        response = requests.get(session_url, timeout=10)

        if response.status_code == 200:
            return True

        response_text = (response.text or "").strip()

        # La centrale puo rispondere con 500 se l'utente ha gia una sessione attiva.
        # In questo caso consideriamo comunque la sessione valida.
        if response.status_code == 500 and "user already logged in" in response_text.lower():
            _LOGGER.debug("Sessione AVS gia attiva per l'utente %s", user)
            return True

        _LOGGER.error(
            "Errore apertura sessione AVS: status=%s body=%s",
            response.status_code,
            response_text,
        )
        return False
    except requests.RequestException as e:
        _LOGGER.error(f"Errore nella chiamata di apertura sessione: {e}")
        return False


def get_zone_status(ip, port, user, pid, zone):
    """
    Ottieni lo stato di una zona specifica.
    """
    status_url = f"http://{ip}:{port}/info/zone?ultra=kOU9Rc885y1Gia3p&pid={pid}&user={user}&zone={zone}"
    try:
        response = requests.get(status_url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get('status', 'unknown')
        else:
            _LOGGER.error(f"Errore: {response.status_code}, {response.text}")
            return "Error: Unable to retrieve zone status"
    except requests.RequestException as e:
        _LOGGER.error(f"Errore nella chiamata API per la zona: {e}")
        return "Error"


def get_sector_status(ip, port, user, pid, sector):
    """
    Ottieni lo stato di un settore specifico.
    """
    status_url = f"http://{ip}:{port}/info/sector?ultra=kOU9Rc885y1Gia3p&pid={pid}&user={user}&sector={sector}"
    try:
        response = requests.get(status_url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            sector_key = f"sect-{sector:02d}"
            if sector_key in data:
                return data.get(sector_key, "unknown")
            if "status" in data:
                return data.get("status", "unknown")
            return next(iter(data.values()), "unknown")
        else:
            _LOGGER.error(f"Errore: {response.status_code}, {response.text}")
            return "Error: Unable to retrieve sector status"
    except requests.RequestException as e:
        _LOGGER.error(f"Errore nella chiamata API per il settore: {e}")
        return "Error"
        
def edit_sector_status(ip, port, user, pid, sector, command):
    """
    Modifica lo stato di un settore specifico.
    """
    status_url = f"http://{ip}:{port}/cmd/sector/{command}?ultra=kOU9Rc885y1Gia3p&pid={pid}&user={user}&sector={sector}"
    try:
        response = requests.get(status_url, timeout=10)
        if response.status_code == 200:
            return True
        else:
            _LOGGER.error(f"Errore: {response.status_code}, {response.text}")
            return False
    except requests.RequestException as e:
        _LOGGER.error(f"Errore nella chiamata API per il settore: {e}")
        return False

class AVSAlarmCoordinator(DataUpdateCoordinator):
    """AVS Alarm coordinator."""

    def __init__(
        self,
        hass: HomeAssistant,
        ip: str,
        port: int,
        user: str,
        pid: str,
        num_sectors: int = 1,
        update_interval: int = 30,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="AVS Alarm",
            update_interval=timedelta(seconds=update_interval),
        )
        self.ip = ip
        self.port = port
        self.user = user
        self.pid = pid
        self.num_sectors = num_sectors

    async def _async_update_data(self) -> dict[str, Any]:
        """Update data via API."""
        try:
            # Ignoriamo il risultato di open_session
            await self.hass.async_add_executor_job(
                open_session,
                self.ip,
                self.port,
                self.user,
                self.pid,
            )

            new_data = {}
            for sector in range(1, self.num_sectors + 1):
                sector_status = await self.hass.async_add_executor_job(
                    get_sector_status,
                    self.ip,
                    self.port,
                    self.user,
                    self.pid,
                    sector,
                )
                new_data[f"sector_{sector}"] = sector_status
            
            # Se i dati sono cambiati, notifica tutti i listener
            if self.data != new_data:
                self.async_set_updated_data(new_data)
            
            return new_data

        except Exception as err:
            _LOGGER.error("Error updating AVS alarm data: %s", err)
            return self.data or {
                f"sector_{sector}": "unknown"
                for sector in range(1, self.num_sectors + 1)
            }
