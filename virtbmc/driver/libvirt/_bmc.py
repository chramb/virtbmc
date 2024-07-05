#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from __future__ import annotations

import contextlib
import logging
import xml.etree.ElementTree as ET
from typing import TYPE_CHECKING, Unpack

import libvirt

from virtbmc.core import Bmc
from virtbmc.core.constants import IPMI_COMPLETION_CODES as CODE
from virtbmc.exception import VirtBmcDriverError

if TYPE_CHECKING:
    from typing import Any, Generator, Literal

    from virtbmc.core.types import BmcConfig, ipmi_boot_device

GET_BOOT_DEVICES_MAP: dict[str, int] = {
    "network": 4,
    "hd": 8,
    "cdrom": 0x14,
}

SET_BOOT_DEVICES_MAP = {
    "network": "network",
    "hd": "hd",
    "optical": "cdrom",
}


class LibvirtBMC(Bmc):
    driver: str = "libvirt"

    def __init__(
        self,
        *,
        readonly: bool = False,
        **kwargs: Unpack[BmcConfig],
    ) -> None:
        super().__init__(**{k: v for k, v in kwargs.items() if v is not None})

        self._readonly = readonly

        if kwargs.get("properties").get("libvirt_uri") is None:
            kwargs["properties"]["libvirt_uri"] = "qemu:///system"

        self.log = self.log or logging.getLogger(f"virtbmc.driver.libvirt.{self.name}")

    @contextlib.contextmanager
    def _connect(self) -> Generator[libvirt.virConnect, Any, None]:
        try:
            if self.properties.get("libvirt_sasl_username") and self.properties.get("libvirt_sasl_password"):

                def request_cred(credentials: Any, user_data: Any) -> Literal[0]:
                    for credential in credentials:
                        if credential[0] == libvirt.VIR_CRED_AUTHNAME:
                            credential[4] = self.properties["libvirt_sasl_username"]
                        elif credential[0] == libvirt.VIR_CRED_PASSPHRASE:
                            credential[4] = self.password
                    return 0

                auth = [[libvirt.VIR_CRED_AUTHNAME, libvirt.VIR_CRED_PASSPHRASE], request_cred, None]
                flags = libvirt.VIR_CONNECT_RO if self._readonly else 0
                conn = libvirt.openAuth(self.properties["libvirt_uri"], auth, flags)  # type: ignore
            elif self._readonly:
                conn = libvirt.openReadOnly(self.properties["libvirt_uri"])
            else:
                conn = libvirt.open(self.properties["libvirt_uri"])
        except libvirt.libvirtError as e:
            raise VirtBmcDriverError(str(e)) from e
        try:
            yield conn
        finally:
            conn.close()

    # BMC Operations
    # ref: 28.3 Chassis Control Command: https://www.intel.com/content/dam/www/public/us/en/documents/specification-updates/ipmi-intelligent-platform-mgt-interface-spec-2nd-gen-v2-0-spec-update.pdf
    def is_active(self) -> bool:
        with self._connect() as conn:
            domain = conn.lookupByName(self.name)
            return domain.isActive()

    def cold_reset(self) -> CODE:
        self.log.debug("cold_reset: called, stopping BMC")
        self.stop()
        return CODE.SUCCESS

    def get_power_state(self) -> Literal["on", "off"]:
        self.log.debug("get_power_state: called")
        return "on" if self.is_active() else "off"

    def power_off(self) -> CODE:
        with self._connect() as conn:
            domain = conn.lookupByName(self.name)
            if self.is_active():
                domain.destroy()

        return CODE.SUCCESS

    def power_on(self) -> CODE:
        with self._connect() as conn:
            domain = conn.lookupByName(self.name)
            if not self.is_active():
                domain.create()

        return CODE.SUCCESS

    def power_reset(self) -> CODE:
        with self._connect() as conn:
            domain = conn.lookupByName(self.name)
            domain.reset()

        return CODE.SUCCESS

    def power_cycle(self) -> CODE:
        with self._connect() as conn:
            domain = conn.lookupByName(self.name)
            domain.reboot()

        return CODE.SUCCESS

    def power_shutdown(self) -> CODE:
        with self._connect() as conn:
            domain = conn.lookupByName(self.name)
            if self.is_active():
                domain.shutdown()

        return CODE.SUCCESS

    def get_boot_device(self) -> ipmi_boot_device:
        with self._connect() as conn:
            domain = conn.lookupByName(self.name)
            boot_element = ET.fromstring(domain.XMLDesc()).find(".//os/boot")
            if boot_element is not None:
                boot_dev = boot_element.attrib.get("dev")
                return boot_dev if boot_dev in ("network", "hd", "cdrom") else "default"

            return "default"

    def set_boot_device(self, bootdevice: ipmi_boot_device) -> None | CODE:
        device = SET_BOOT_DEVICES_MAP.get(bootdevice)
        try:
            with self._connect() as conn:
                domain = conn.lookupByName(self.name)
                tree = ET.fromstring(domain.XMLDesc())

                # Remove all "boot" element under "devices"
                # They are mutually exclusive with "os/boot"
                for device_element in tree.findall("devices/*"):
                    for boot_element in device_element.findall("boot"):
                        device_element.remove(boot_element)

                for os_element in tree.findall("os"):
                    # Remove all "boot" elements under "os"
                    for boot_element in os_element.findall("boot"):
                        os_element.remove(boot_element)

                    # Add a new boot element with the request boot device
                    boot_element = ET.SubElement(os_element, "boot")
                    boot_element.set("dev", device)  # type: ignore

                conn.defineXML(ET.tostring(tree, encoding="unicode"))

        except Exception:
            # Command failed, but let client to retry
            return CODE.NODE_BUSY
