# VirtBMC OpenStack Driver
a driver for VirtBMC to interact with OpenStack Clouda

# Installation

## From Source

Clone this repo and enter it.
```shell
git clone https://github.com/chramb/virtbmc.git && cd virtbmc/
```

Install core (common dependencies) and the driver itself.
```shell
pip install --user ./virtbmc_core ./virtbmc_openstack
```

Check module is available.
```shell
python -m virtbmc_openstack --version
0.1.dev
```

## Usage - Standalone
Individual drivers can be used without virtbmc itself for that reason
 containers containing just them are also created.

To use such container just use the container (`ghcr.io/chramb/virtbmc-openstack`)
 instead of python module itself

> [!NOTE]
> Access to openstack cloud is done through openstacksdk,
> therefore you need to provade appropriate environment variables 
> or `clouds.yaml` config file and specify `--os-cloud`

### From Commandline
```shell
python -m virtbmc_openstack \
    --os-cloud openstack \
    --username admin \
    --password password \
    --port 6230 \
    e507dd77-1ae4-4fd8-9c1e-47e0252a7b2b
```

### As systemd Service
```ini
# /etc/systemd/system/virtbmc-openstack-example.service
[Unit]
Description=A service file for VirtBMC Openstack Driver managing 'e507dd77-1ae4-4fd8-9c1e-47e0252a7b2b'

[Service]
ExecStart=python -m virtbmc_openstack --os-cloud openstack --port 6230 e507dd77-1ae4-4fd8-9c1e-47e0252a7b2b

[Install]
WantedBy=multi-user.target
```
