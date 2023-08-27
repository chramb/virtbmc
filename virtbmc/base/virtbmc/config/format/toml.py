from __future__ import annotations

try:
    import tomli_w  # pyright: ignore[reportMissingImports]
except ImportError:
    raise ImportError("Missing tomli-w module")

try:
    import tomllib  # pyright: ignore[reportMissingImports]
except ImportError:
    try:
        import tomli as tomllib  # pyright: ignore[reportMissingImports]
    except:
        raise ImportError("Missing tomli module")


from typing import TYPE_CHECKING, Any, Dict

if TYPE_CHECKING:
    from pathlib import Path


def write(config: Dict[str, Any], file: Path) -> None:
    with file.open("wb") as f:
        tomli_w.dump(config, f)
        return


def read(file: Path) -> Dict[str, Any]:
    with file.open("rb") as f:
        return tomllib.load(f)
