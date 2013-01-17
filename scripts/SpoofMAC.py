#!/usr/bin/env python
# -*- coding: utf8 -*-
"""SpoofMAC

Usage:
    SpoofMAC.py list [--wifi]
    SpoofMAC.py randomize [--local] <devices>...
    SpoofMAC.py set <mac> <devices>...
    SpoofMAC.py reset <devices>...
    SpoofMAC.py -h | --help
    SpoofMAC.py --version

Options:

    -h --help       Shows this message.
    --version       Show package version.
    --wifi          Try to only show wireless interfaces.
    --local         Set the locally administered flag on randomized MACs.
"""
import sys

from docopt import docopt

from spoofmac.version import __version__
from spoofmac.util import random_mac_address, MAC_ADDRESS_R
from spoofmac.interface import (
    wireless_port_names,
    find_interfaces,
    find_interface,
    set_interface_mac
)


def list_interfaces(args):
    targets = []

    # Should we only return prospective wireless interfaces?
    if args['--wifi']:
        targets += wireless_port_names

    for port, device, address in find_interfaces(targets=targets):
        line = []
        line.append('- "{port}"'.format(port=port))
        line.append('on device "{device}"'.format(device=device))
        if address:
            line.append('with MAC address {mac}'.format(mac=address))

        print(' '.join(line))


def main(args):
    if args['list']:
        list_interfaces(args)
    elif args['randomize'] or args['set'] or args['reset']:
        for target in args['<devices>']:
            # Fill out the details for `target`, which could be a Hardware
            # Port or a literal device.
            result = find_interface(target)
            if result is None:
                print('- couldn\'t find the device for {target}'.format(
                    target=target
                ))
                return 1

            port, device, address = result
            if args['randomize']:
                target_mac = random_mac_address(args['--local'])
            elif args['set']:
                target_mac = args['<mac>']
            elif args['reset']:
                if address is None:
                    print('- {target} missing hardware MAC'.format(
                        target=target
                    ))
                    continue
                target_mac = address

            if not MAC_ADDRESS_R.match(target_mac):
                print('- {mac} is not a valid MAC address'.format(
                    mac=target_mac
                ))
                return 1

            set_interface_mac(port, device, address, target_mac)

    return 1


if __name__ == '__main__':
    arguments = docopt(__doc__, version=__version__)
    sys.exit(main(arguments))
