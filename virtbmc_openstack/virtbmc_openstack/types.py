from __future__ import annotations

from typing import Literal, TypedDict

# fmt: off
status = Literal[
    "ACTIVE", "BUILDING", "DELETED", "ERROR", "HARD_REBOOT", "PASSWORD",
    "PAUSED", "REBOOT", "REBUILD", "RESCUED", "RESIZED", "REVERT_RESIZE",
    "SHUTOFF", "SOFT_DELETED", "STOPPED", "SUSPENDED", "UNKNOWN",
    "VERIFY_RESIZE"]
vm_state = Literal[
    "active", "building", "paused", "suspended", "stopped", "rescued", "resized",
    "soft_deleted", "deleted", "error", "shelved", "shelved_offloaded"]
task_state = Literal[
    "scheduling", "block_device_mapping", "networking", "spawning",
    "image_snapshot", "image_snapshot_pending", "image_pending_upload",
    "image_uploading", "image_backup", "updating_password", "resize_prep",
    "resize_migrating", "resize_migrated", "resize_finish", "resize_reverting",
    "resize_confirming", "rebooting", "reboot_pending", "reboot_started",
    "rebooting_hard", "reboot_pending_hard", "reboot_started_hard", "pausing",
    "unpausing", "suspending", "resuming", "powering-off", "powering-on",
    "rescuing", "unrescuing", "rebuilding", "rebuild_block_device_mapping",
    "rebuild_spawning", "migrating", "deleting", "soft-deleting", "restoring",
    "shelving", "shelving_image_pending_upload", "shelving_image_uploading",
    "shelving_offloading", "unshelving"]
# fmt: on


class Config(TypedDict):
    driver: Literal["openstack"]
    name: str
    username: str
    password: str
    port: int
    address: str
