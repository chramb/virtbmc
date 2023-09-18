import argparse

from virtbmc_core.cli import bmc_options


def test_bmc_options() -> None:
    # TODO: parametrize and test invalid args
    ap = argparse.ArgumentParser()
    ap, ag = bmc_options(ap)
    assert ag.title == "VirtBMC Options"
    args = ap.parse_args("")
    assert args.username == "admin"
    assert args.password == "password"
    assert args.port == 623
    assert args.address == "::"
