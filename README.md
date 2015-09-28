NSX Version Matcher for Palo Alto Networks NGFW
===============================================

Overview
--------

This script automatically upgrades any firewalls in an NSX environment so 
that all firewalls on all ESX hosts have the same PAN-OS version.  It can be 
run as a cron job or using VMware Orchestrator tools like VRA or VRO to
trigger on new host addition.

The script automatically determines which Panorama device-group contains
the NSX firewalls, and which version of PAN-OS they should be running.  The 
target version of PAN-OS for all upgrades is the version that more than 50% 
of the NSX firewalls are running.  All intermediate upgrades to get to the 
target version and all reboots after upgrades are handled automatically.  
Firewalls are never downgraded by this script, only upgraded.

Author
------

[Brian Torres-Gil](https://github.com/btorresgil)

Dependencies
------------

Two python libraries are required:

pan-python - https://github.com/ksteves/pan-python

pandevice - https://github.com/PaloAltoNetworks-BD/pandevice

Install Dependencies
--------------------

This install process will be easier in the future.

pan-python:

    pip install pan-python==0.7.0

pandevice:

    # if using git:
    git clone https://github.com/PaloAltoNetworks-BD/pandevice.git
    cd pandevice
    
    # if not using git:
    wget -O pandevice.zip https://github.com/PaloAltoNetworks-BD/pandevice/archive/master.zip
    unzip pandevice.zip
    cd pandevice-master
    
    # after downloading the library, install it:
    python setup.py install
    
Download This Script
--------------------
    
    # if using git:
    git clone https://github.com/PaloAltoNetworks-BD/nsx-ngfw-version-match.git
    cd nsx-ngfw-version-match
    
    # if not using git:
    wget https://raw.githubusercontent.com/PaloAltoNetworks-BD/nsx-ngfw-version-match/master/nsx-ngfw-version-match.py
    
Usage
-----

Before running the script, edit it and set the variables in the section 
called "Modify these settings".  This includes your Panorama login settings 
and logging and error settings.

The script is self-contained, so simply run it from the command line or from
a cron job or orchestration tool.  If all NSX firewalls are running the 
same version, the script will do nothing and exit, so it is safe to run it 
repeatedly.

Run the script:

    python nsx-ngfw-version-match.py
   
Security
--------
   
A note about security.  This script contains your Panorama credentials, so it
is recommended to have the script owned by a specific user with limited  
access, and remove all permissions incuding read permissions for other users.

For example:

    chown limiteduser:limitedgroup nsx-ngfw-version-match.py
    chmod go-rwx nsx-ngfw-version-match.py
    
Non-NSX environments
--------------------

This script is exclusive to NSX environments, but the same libraries 
(pan-python and pandevice) can be used to upgrade a single firewall in a 
non-NSX environment.  The script for this is available in the pandevice
library:

https://github.com/PaloAltoNetworks-BD/pandevice/tree/master/examples
