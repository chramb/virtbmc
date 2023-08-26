from virtbmc_core.driver.dummy.cmd import dummy_commands
from virtbmc_core.driver.dummy.config import DummyBmcConfig
from virtbmc_core.driver.dummy.driver import DummyBMC

bmcConfig = DummyBmcConfig
cmd = dummy_commands
driver = DummyBMC
