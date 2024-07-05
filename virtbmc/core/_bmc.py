from __future__ import annotations

import logging
import struct
import traceback
from ipaddress import ip_address
from typing import TYPE_CHECKING, Any, Literal

import pyghmi.ipmi.command as _ipmicommand
import pyghmi.ipmi.console as _console
import pyghmi.ipmi.private.serversession as _serversession
import pyghmi.ipmi.private.session as _ipmisession

from virtbmc.config import get_config_value
from virtbmc.core.constants import IPMI_COMPLETION_CODES as CODE
from virtbmc.exception import VirtBmcError

if TYPE_CHECKING:
    from uuid import UUID

    from virtbmc.core.types import BmcConfig, IPMIRequest, ipmi_boot_device

log = logging.getLogger(__package__)


class Bmc(_serversession.IpmiServer):
    driver: str = ""
    activated: bool = False
    sol: _console.ServerConsole | None = None
    iohandler = None

    def __init__(
        self,
        *,
        name: str,
        username: str = get_config_value("bmc.username"),  # type: ignore
        password: str = get_config_value("bmc.password"),  # type: ignore
        port: int = get_config_value("bmc.port"),  # type: ignore
        address: str = get_config_value("bmc.address"),  # type: ignore
        properties: dict[str, Any] = get_config_value("bmc.properties"),
        log: logging.Logger = log,
        **kwargs: Any,
    ) -> None:
        self._stopped: bool = False
        self.log = log

        self.name = name
        self.username = username
        self.password = password
        self.properties = {**properties, **kwargs} if kwargs else properties

        if name is None:  # type: ignore
            msg = "Invalid argument 'name' can't be None"
            raise ValueError(msg)

        try:
            self.port = int(port)
        except ValueError:
            msg = "Invalid argument for port parameter"
            self.log.exception(msg)
            raise ValueError(msg)

        if self.port < 0 or self.port > 65535:
            msg = "Invalid value in the port parameter"
            self.log.exception(msg)
            raise ValueError(msg)

        try:
            self.address = str(ip_address(address))
        except ValueError:
            msg = "Invalid value in the ip address field"
            self.log.exception(msg)
            raise ValueError(msg)

    def start(self, timeout: int = 30) -> None:
        log.debug(f"{self.name}:start() called")
        super().__init__(
            authdata={self.username: self.password},
            port=self.port,
            address=self.address,
        )

        while not self._stopped:
            _ipmisession.Session.wait_for_rsp(timeout)  # type: ignore # pragma: no cover

    def stop(self) -> None:
        log.debug(f"{self.name}:stop() called")
        self._stopped = True

    def config(self) -> BmcConfig:
        return {
            "name": self.name,
            "driver": self.driver,
            "username": self.username,
            "password": self.password,
            "address": self.address,
            "port": self.port,
            "properties": self.properties,
        }

    def get_system_guid(self) -> UUID:
        raise NotImplementedError

    def cold_reset(self) -> CODE:
        raise NotImplementedError

    def power_off(self) -> CODE:
        raise NotImplementedError

    def power_on(self) -> CODE:
        raise NotImplementedError

    def power_cycle(self) -> CODE:
        raise NotImplementedError

    def power_reset(self) -> CODE:
        raise NotImplementedError

    def pulse_diag(self) -> CODE:
        raise NotImplementedError

    def power_shutdown(self) -> CODE:
        raise NotImplementedError

    def get_power_state(self) -> Literal["on", "off"]:  # TODO: remove this
        return "on" if self.is_active() else "off"

    def is_active(self) -> bool:
        raise NotImplementedError

    def activate_payload(self, request: IPMIRequest, session: _serversession.ServerSession) -> None:
        if self.iohandler is None or not self.is_active():
            session.send_ipmi_response(code=0x81)
        elif self.activated:
            session.send_ipmi_response(code=0x80)
        else:
            self.activated = True
            solport = list(struct.unpack("BB", struct.pack("!H", self.port)))
            session.send_ipmi_response(data=[0, 0, 0, 0, 1, 0, 1, 0, *solport, 255, 255])  # type: ignore
            self.sol = _console.ServerConsole(session, self.iohandler)

    def deactivate_payload(self, request: IPMIRequest, session: _serversession.ServerSession) -> None:
        if self.iohandler is None:
            session.send_ipmi_response(code=0x81)
        elif not self.activated:
            session.send_ipmi_response(code=0x80)
        else:
            session.send_ipmi_response()
            if self.sol is not None:
                self.sol.close()
                self.activated = False
                self.sol = None

    @staticmethod
    def handle_missing_command(session: _serversession.ServerSession) -> None:
        session.send_ipmi_response(code=0xC1)

    def get_chassis_status(self, session: _serversession.ServerSession) -> None:
        try:
            log.debug(f"{self.name}:get_power_state(): called")
            powerstate = self.get_power_state()
        except NotImplementedError:
            return session.send_ipmi_response(code=0xC1)
        if powerstate in _ipmicommand.power_states:
            powerstate = _ipmicommand.power_states[powerstate]
        if powerstate not in (0, 1):
            raise VirtBmcError("BMC implementation mistake")
        statusdata = bytearray([powerstate, 0, 0])
        session.send_ipmi_response(data=statusdata)

    def control_chassis(self, request: IPMIRequest, session: _serversession.ServerSession) -> None:
        rc: CODE = CODE.SUCCESS
        try:
            directive = request["data"][0]
            if directive == 0:
                log.debug(f"{self.name}:power_off(): called")
                rc = self.power_off()
            elif directive == 1:
                log.debug(f"{self.name}:power_on(): called")
                rc = self.power_on()
            elif directive == 2:
                log.debug(f"{self.name}:power_cycle(): called")
                rc = self.power_cycle()
            elif directive == 3:
                log.debug(f"{self.name}:power_reset(): called")
                rc = self.power_reset()
            elif directive == 4:
                # i.e. Pulse a diagnostic interrupt(NMI) directly
                log.debug(f"{self.name}:pulse_diag(): called")
                rc = self.pulse_diag()
            elif directive == 5:
                log.debug(f"{self.name}:power_shutdown(): called")
                rc = self.power_shutdown()
            session.send_ipmi_response(code=rc)
        except NotImplementedError:
            session.send_ipmi_response(code=0xCC)
        except KeyError:
            session.send_ipmi_response(code=0xCC)

    def get_boot_device(self) -> ipmi_boot_device | int:
        raise NotImplementedError

    def get_system_boot_options(self, request: IPMIRequest, session: _serversession.ServerSession) -> None:
        if request["data"][0] == 5:  # boot flags
            try:
                log.debug(f"{self.name}:get_boot_device(): called")
                bootdevice: ipmi_boot_device | int = self.get_boot_device()
            except NotImplementedError as e:
                log.error(e)
                session.send_ipmi_response(data=bytearray([1, 5, 0, 0, 0, 0, 0]))
                return
            if bootdevice is not int:
                try:
                    bootdevice = _ipmicommand.boot_devices[bootdevice]  # TODO: convert to StrEnum
                except KeyError:
                    session.send_ipmi_response(data=bytearray([1, 5, 0, 0, 0, 0, 0]))
            paramdata = [1, 5, 0b10000000, bootdevice, 0, 0, 0]
            return session.send_ipmi_response(data=paramdata)  # type: ignore
        else:
            session.send_ipmi_response(code=0x80)

    def set_boot_device(self, bootdevice: ipmi_boot_device) -> None | CODE:
        raise NotImplementedError

    def set_system_boot_options(self, request: IPMIRequest, session: _serversession.ServerSession) -> None:
        if request["data"][0] in (0, 3, 4):
            # for now, just smile and nod at boot flag bit clearing
            # implementing it is a burden and implementing it does more to
            # confuse users than serve a useful purpose
            session.send_ipmi_response()
        elif request["data"][0] == 5:
            bootdevice = (request["data"][2] >> 2) & 0b1111
            try:
                bootdevice = _ipmicommand.boot_devices[bootdevice]
            except KeyError:
                session.send_ipmi_response(code=0xCC)
                return
            log.debug(f"{self.name}:set_boot_device(): called")
            self.set_boot_device(bootdevice)
            session.send_ipmi_response()
        else:
            raise NotImplementedError

    def handle_raw_request(self, request: IPMIRequest, session: _serversession.ServerSession) -> None:
        try:
            if request["netfn"] == 6:
                if request["command"] == 1:  # get device id
                    return self.send_device_id(session)  # type: ignore
                elif request["command"] == 2:  # cold reset
                    log.debug(f"{self.name}:cold_reset(): called")
                    return session.send_ipmi_response(code=self.cold_reset())
                elif request["command"] == 0x37:  # get system guid
                    log.debug(f"{self.name}:get_system_guid(): called")
                    guid = self.get_system_guid()
                    return session.send_ipmi_response(code=0x00, data=guid.bytes_le)
                elif request["command"] == 0x48:  # activate payload
                    log.debug(f"{self.name}:activate_payolad(): called")
                    return self.activate_payload(request, session)
                elif request["command"] == 0x49:  # deactivate payload
                    log.debug(f"{self.name}:deactivate_payolad(): called")
                    return self.deactivate_payload(request, session)
            elif request["netfn"] == 0:
                if request["command"] == 1:  # get chassis status
                    return self.get_chassis_status(session)
                elif request["command"] == 2:  # chassis control
                    return self.control_chassis(request, session)
                elif request["command"] == 8:  # set boot options
                    return self.set_system_boot_options(request, session)
                elif request["command"] == 9:  # get boot options
                    return self.get_system_boot_options(request, session)
            session.send_ipmi_response(code=CODE.INVALID_COMMAND)
        except NotImplementedError:
            session.send_ipmi_response(code=CODE.INVALID_COMMAND)
        except Exception:
            session.send_ipmi_response(code=CODE.UNSPECIFIED)
            traceback.print_exc()
