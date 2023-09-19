import argparse

from virtbmc_core.bmc import Bmc


def test_bmc_options() -> None:
    # TODO: parametrize and test invalid args
    ap = argparse.ArgumentParser()
    ap = Bmc.cli(ap)
    args = ap.parse_args("")
    assert args.username == "admin"
    assert args.password == "password"
    assert args.port == 623
    assert args.address == "::"
