"""Sensor platform for HACS."""
# pylint: disable=unused-argument
from integrationhelper import Logger
from homeassistant.helpers.entity import Entity
from aiogithubapi import AIOGitHubException
from .hacsbase import Hacs as hacs
from .const import DOMAIN, VERSION, NAME_LONG


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Setup sensor platform."""
    async_add_entities([HACSSensor()])


async def async_setup_entry(hass, config_entry, async_add_devices):
    """Setup sensor platform."""
    async_add_devices([HACSSensor()])


class HACSSensor(Entity):
    """HACS Sensor class."""

    def __init__(self):
        """Initialize."""
        self._state = None
        self.logger = Logger("hacs.sensor")
        self.has_update = []

    async def async_update(self):
        """Update the sensor."""
        if hacs.system.status.background_task:
            return

        updates = 0
        has_update = []
        prev_has_update = self.has_update

        for repository in hacs.repositories:
            if repository.status.pending.upgrade:
                if repository.information.uid not in prev_has_update:
                    try:
                        await repository.update_repository()
                        if repository.status.pending.upgrade:
                            hacs.logger.debug(repository.information.full_name)
                            updates += 1
                            has_update.append(repository.information.uid)
                    except AIOGitHubException:
                        pass

        self._state = updates
        self.has_update = has_update

    @property
    def unique_id(self):
        """Return a unique ID to use for this sensor."""
        return (
            "0717a0cd-745c-48fd-9b16-c8534c9704f9-bc944b0f-fd42-4a58-a072-ade38d1444cd"
        )

    @property
    def name(self):
        """Return the name of the sensor."""
        return "hacs"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return "mdi:package"

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return "pending update(s)"

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.unique_id)},
            "name": NAME_LONG,
            "sw_version": VERSION,
        }
