from __future__ import annotations

import logging
import urllib.parse
from typing import TYPE_CHECKING, Literal, Unpack

import amt.client
import amt.wsman

from virtbmc.core import Bmc
from virtbmc.core.constants import IPMI_COMPLETION_CODES as CODE

if TYPE_CHECKING:
    from virtbmc.core.types import BmcConfig, ipmi_boot_device

log = logging.getLogger("virtbmc.driver.amt")


class AMTBMC(Bmc):
    driver: str = "amt"

    def __init__(self, **kwargs: Unpack[BmcConfig]) -> None:
        super().__init__(**{k: v for k, v in kwargs.items() if v is not None})

        if (amt_host := self.properties.get("amt_host")) is None:
            msg = "missing required property 'amt_host'"
            raise TypeError(msg)

        url: urllib.parse.SplitResult = urllib.parse.urlsplit(amt_host)
        address = url.netloc.split(":")[0] if ":" in url.netloc else url.netloc

        self._client = amt.client.Client(
            address=address,
            protocol=url.scheme or "http",
            username=self.properties.get("amt_username"),
            password=self.properties["amt_password"],
        )
        self.properties["amt:last_boot_dev"] = None

    def _set_boot_device(self, bootdevice: ipmi_boot_device) -> None:
        bootdev: Literal["pxe", "hd", "cd"]
        if bootdevice in ["net", "network", "pxe"]:
            bootdev = "pxe"
        elif bootdevice in ["cdrom", "optical", "dvd"]:
            bootdev = "cd"
        else:
            bootdev = "hd"

        amt.wsman.change_boot_order_request(self._client.path, bootdev)
        amt.wsman.enable_boot_config_request(self._client.path)

    # BMC Operations
    # ref: 28.3 Chassis Control Command: https://www.intel.com/content/dam/www/public/us/en/documents/specification-updates/ipmi-intelligent-platform-mgt-interface-spec-2nd-gen-v2-0-spec-update.pdf
    def is_active(self) -> bool:
        # 2 = on
        # 8 = off
        return str(amt.wsman.POWER_STATES["on"]) == self._client.power_status()

    def cold_reset(self) -> CODE:
        self.stop()
        return CODE.SUCCESS

    def get_power_state(self) -> Literal["on", "off"]:
        return "on" if self.is_active() else "off"

    def power_off(self) -> CODE:
        self._client.power("off")

        return CODE.SUCCESS

    def power_on(self) -> CODE:
        if self.properties["amt:last_boot_device"] is None:
            self._client.power("on")
            return CODE.SUCCESS

        self._set_boot_device(self.properties["amt:last_boot_device"])
        self._client.power("on")

        return CODE.SUCCESS

    def power_reset(self) -> CODE:
        self._client.power("reboot")

        return CODE.SUCCESS

    def power_cycle(self) -> CODE:
        self._client.power("hard-reboot")

        return CODE.SUCCESS

    def power_shutdown(self) -> CODE:
        self._client.power("hard-reboot")

        return CODE.SUCCESS

    def get_boot_device(self) -> ipmi_boot_device:
        return self.properties["amt:last_boot_device"] or "hd"

    def set_boot_device(self, bootdevice: ipmi_boot_device) -> CODE:
        if self.properties["amt:last_boot_device"] == bootdevice:
            return CODE.SUCCESS

        if bootdevice in ("net", "network", "pxe", "cdrom", "optical", "dvd"):
            self.properties["amt:last"] = bootdevice
            return CODE.SUCCESS
        else:
            return CODE.INVALID_DATA_FIELD_IN_REQUEST
