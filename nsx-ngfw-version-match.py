#!/usr/bin/env python

"""Match versions for NSX firewalls

Logs into Panorama and gets all firewalls from the NSX device-group.
Checks if there is a version that more than 50% of firewalls are running,
then upgrades any firewalls not running that version to that version.

"""

###
### Imports
###

import sys
import logging
from collections import Counter
from distutils.version import StrictVersion
from pprint import pformat
from pandevice import errors
from pandevice.firewall import Firewall
from pandevice.panorama import Panorama
from pan.xapi import PanXapiError

###
### Modify these settings
###

# Panorama connection settings
PANORAMA_HOSTNAME = "10.0.0.1"
PANORAMA_USERNAME = "admin"
PANORAMA_PASSWORD = "admin"

# Logging level (DEBUG or INFO or WARN)
DEBUG_LEVEL = logging.INFO

# Stop the entire script if there's an error upgrading
# a firewall.  If False, an error will cause the problem firewall
# to be skipped and the next firewall will be upgraded.
# Recommended setting is True
STOP_ON_ERROR = True

###
### Script
###

def main():

    # Enable logging to terminal

    logging.basicConfig(level=DEBUG_LEVEL)

    # Create the connection to Panorama

    panorama = Panorama(
        PANORAMA_HOSTNAME,
        443,
        PANORAMA_USERNAME,
        PANORAMA_PASSWORD,
        classify_exceptions=True
    )

    # Get the NSX Device Group

    logging.info("Logging in to Panorama at %s" % PANORAMA_HOSTNAME)

    nsxdg_xpath = "/config/devices/entry[@name='localhost.localdomain']/vmware-service-manager/device-group"

    try:
        panorama.xapi.show(nsxdg_xpath)
        nsx_device_group = panorama.xapi.element_root.find("./result/device-group").text
        logging.info("NSX device-group found: %s" % nsx_device_group)
    except (errors.PanDeviceXapiError, AttributeError) as e:
        logging.warn("Cannot determine NSX device-group setting: %s" % e.message)
        sys.exit(1)

    # Get the list of devices and device-groups from Panorama

    devices = panorama.refresh_devices_from_panorama()
    logging.debug("Devices: %s" % pformat(devices))

    # Filter to a list of devices in the NSX device group

    devices = [device for device in devices.values() if device['devicegroup'] == nsx_device_group]
    logging.debug("Devices in NSX device-group:")
    for device in devices:
        logging.debug("Device: %s  -  Version: %s" % (device['ip-address'], device['sw-version']))

    # Determine which version more than 50% of the devices are running

    versions_list = [device['sw-version'] for device in devices]
    most_common_versions = Counter(versions_list).most_common(2)
    if len(most_common_versions) == 0:
        logging.warn("No firewalls found in device group: %s" % nsx_device_group)
        sys.exit(1)
    elif len(most_common_versions) == 1:
        logging.info("All firewalls are running version %s, no upgrade needed" % most_common_versions[0][0])
        sys.exit(0)
    elif most_common_versions[0][1] == most_common_versions[1][1]:
        logging.warn("There are an equal number of firewalls running different version."
                     "Can't determine which version to upgrade to.")
        sys.exit(1)

    target_version = most_common_versions[0][0]
    logging.info("Determined target version: %s" % target_version)

    # Filter to a list of devices not running the most common version

    non_target_devices = [device for device in devices if device['sw-version'] != target_version]

    # Filter to only device below the target version, ignore devices above target version (do not downgrade)

    target_version = StrictVersion(target_version)
    for device in non_target_devices:
        device['sw-version'] = StrictVersion(device['sw-version'])
    upgrade_devices = [device for device in devices if device['sw-version'] < target_version]

    # For each device, upgrade to the most common version

    for device in upgrade_devices:
        try:
            # Connect to the device through Panorama to trigger an upgrade
            # (do not use Panorama batch upgrade)
            pandevice = Firewall(PANORAMA_HOSTNAME,
                                 serial=device['serial'],
                                 api_key=panorama.api_key)
            # Upgrade to target version and reboot
            pandevice.software.upgrade_to_version("target_version")
        except PanXapiError as e:
            # Only raise the exception if STOP_ON_ERROR is true.
            # Otherwise continue to the next firewall.
            if STOP_ON_ERROR:
                raise e

if __name__ == "__main__":
    main()

