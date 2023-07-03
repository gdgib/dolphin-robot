from abc import ABC
import logging

from homeassistant.components.number import NumberEntity, NumberEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_STATE, Platform
from homeassistant.core import HomeAssistant

from .common.base_entity import MyDolphinPlusBaseEntity, async_setup_entities
from .common.consts import ACTION_ENTITY_SET_NATIVE_VALUE, ATTR_ATTRIBUTES
from .managers.coordinator import MyDolphinPlusCoordinator

_LOGGER = logging.getLogger(__name__)

CURRENT_DOMAIN = Platform.NUMBER


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
):
    await async_setup_entities(
        hass,
        entry,
        CURRENT_DOMAIN,
        NumberEntityDescription,
        MyDolphinPlusNumberEntity,
        async_add_entities,
    )


class MyDolphinPlusNumberEntity(MyDolphinPlusBaseEntity, NumberEntity, ABC):
    """Representation of a sensor."""

    def __init__(
        self,
        entity_description: NumberEntityDescription,
        coordinator: MyDolphinPlusCoordinator,
    ):
        super().__init__(entity_description, coordinator, CURRENT_DOMAIN)

        self._attr_native_min_value = entity_description.native_min_value
        self._attr_native_max_value = entity_description.native_max_value

    async def async_set_native_value(self, value: float) -> None:
        """Change the selected option."""
        await self.async_execute_device_action(ACTION_ENTITY_SET_NATIVE_VALUE, value)

    def update_component(self, data):
        """Fetch new state parameters for the sensor."""
        if data is not None:
            state = data.get(ATTR_STATE)
            attributes = data.get(ATTR_ATTRIBUTES)

            self._attr_native_value = state
            self._attr_extra_state_attributes = attributes

        else:
            self._attr_native_value = None
