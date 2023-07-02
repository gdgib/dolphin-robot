from abc import ABC
import logging
import sys
from typing import Any

from homeassistant.components.vacuum import StateVacuumEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_MODE, ATTR_STATE, Platform
from homeassistant.core import HomeAssistant

from .common.base_entity import MyDolphinPlusBaseEntity, async_setup_entities
from .common.consts import (
    ACTION_ENTITY_LOCATE,
    ACTION_ENTITY_PAUSE,
    ACTION_ENTITY_RETURN_TO_BASE,
    ACTION_ENTITY_SEND_COMMAND,
    ACTION_ENTITY_SET_FAN_SPEED,
    ACTION_ENTITY_START,
    ACTION_ENTITY_STOP,
    ACTION_ENTITY_TOGGLE,
    ACTION_ENTITY_TURN_OFF,
    ACTION_ENTITY_TURN_ON,
    ATTR_ATTRIBUTES,
)
from .common.entity_descriptions import MyDolphinPlusVacuumEntityDescription
from .managers.coordinator import MyDolphinPlusCoordinator

_LOGGER = logging.getLogger(__name__)

CURRENT_DOMAIN = Platform.VACUUM


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
):
    await async_setup_entities(
        hass,
        entry,
        CURRENT_DOMAIN,
        MyDolphinPlusVacuumEntityDescription,
        MyDolphinPlusLightEntity,
        async_add_entities,
    )


class MyDolphinPlusLightEntity(MyDolphinPlusBaseEntity, StateVacuumEntity, ABC):
    """Representation of a sensor."""

    def __init__(
        self,
        entity_description: MyDolphinPlusVacuumEntityDescription,
        coordinator: MyDolphinPlusCoordinator,
    ):
        super().__init__(entity_description, coordinator, CURRENT_DOMAIN)

        self._attr_supported_features = entity_description.features
        self._attr_fan_speed_list = entity_description.fan_speed_list

    async def async_return_to_base(self, **kwargs: Any) -> None:
        """Set the vacuum cleaner to return to the dock."""
        await self.async_execute_device_action(ACTION_ENTITY_RETURN_TO_BASE)

    async def async_set_fan_speed(self, fan_speed: str, **kwargs: Any) -> None:
        await self.async_execute_device_action(ACTION_ENTITY_SET_FAN_SPEED, fan_speed)

    async def async_start(self) -> None:
        await self.async_execute_device_action(ACTION_ENTITY_START, self.state)

    async def async_stop(self, **kwargs: Any) -> None:
        await self.async_execute_device_action(ACTION_ENTITY_STOP, self.state)

    async def async_pause(self) -> None:
        await self.async_execute_device_action(ACTION_ENTITY_PAUSE, self.state)

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.async_execute_device_action(ACTION_ENTITY_TURN_ON, self.state)

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.async_execute_device_action(ACTION_ENTITY_TURN_OFF, self.state)

    async def async_toggle(self, **kwargs: Any) -> None:
        await self.async_execute_device_action(ACTION_ENTITY_TOGGLE, self.state)

    async def async_send_command(
        self,
        command: str,
        params: dict[str, Any] | list[Any] | None = None,
        **kwargs: Any,
    ) -> None:
        """Send a command to a vacuum cleaner."""
        await self.async_execute_device_action(
            ACTION_ENTITY_SEND_COMMAND, command, params
        )

    async def async_locate(self, **kwargs: Any) -> None:
        """Locate the vacuum cleaner."""
        await self.async_execute_device_action(ACTION_ENTITY_LOCATE)

    def _handle_coordinator_update(self) -> None:
        """Fetch new state parameters for the sensor."""
        try:
            device_data = self.get_data()
            if device_data is not None:
                state = device_data.get(ATTR_STATE)
                attributes = device_data.get(ATTR_ATTRIBUTES)

                fan_speed = attributes.get(ATTR_MODE)

                self._attr_state = state
                self._attr_extra_state_attributes = attributes
                self._attr_fan_speed = fan_speed

            else:
                self._attr_state = None

            self.async_write_ha_state()

        except Exception as ex:
            exc_type, exc_obj, tb = sys.exc_info()
            line_number = tb.tb_lineno

            _LOGGER.error(
                f"Failed to update {self.unique_id}, Error: {ex}, Line: {line_number}"
            )
