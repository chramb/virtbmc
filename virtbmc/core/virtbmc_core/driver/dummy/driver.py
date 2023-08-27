# Copyright 2015 Lenovo
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""this is a quick sample of how to write something that acts like a bmc
to play:
run fakebmc
# ipmitool -I lanplus -U admin -P password -H 127.0.0.1 power status
Chassis Power is off
# ipmitool -I lanplus -U admin -P password -H 127.0.0.1 power on
Chassis Power Control: Up/On
# ipmitool -I lanplus -U admin -P password -H 127.0.0.1 power status
Chassis Power is on
# ipmitool -I lanplus -U admin -P password -H 127.0.0.1 mc reset cold
Sent cold reset command to MC
(fakebmc exits)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING

from virtbmc_core.driver.base import BaseBMC

log = logging.getLogger("virtbmc.driver.dummy")
# TODO: Add logs to every command


@dataclass
class DummyBMC(BaseBMC):
    powerstate: str = "off"
    bootdevice: str = "default"

    def get_boot_device(self):
        return self.bootdevice

    def set_boot_device(self, bootdevice):
        self.bootdevice = bootdevice

    def cold_reset(self):
        # Reset of the BMC, not managed system, here we will exit the demo
        log.info("shutting down in response to BMC cold reset request")
        return 0

    def get_power_state(self):
        log.info("responding to")
        return self.powerstate

    def power_off(self):
        # this should be power down without waiting for clean shutdown
        self.powerstate = "off"
        log.info("abruptly remove power")

    def power_on(self):
        self.powerstate = "on"
        log.info("powered on")

    def power_reset(self):
        pass

    def power_shutdown(self):
        # should attempt a clean shutdown
        log.info("politely shut down the system")
        self.powerstate = "off"

    def is_active(self):
        return self.powerstate == "on"

    def iohandler(self, data):
        log.info(data)
        if self.sol:
            self.sol.send_data(data)
