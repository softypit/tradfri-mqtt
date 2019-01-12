#!/usr/bin/env python

# file        : tradfri/tradfriActions.py
# purpose     : module for controling status of the Ikea tradfri smart lights
#
# author      : harald van der laan
# date        : 2017/04/10
# version     : v1.1.0
#
# changelog   :
# - v1.1.0      refactor for cleaner code                               (harald)
# - v1.0.0      initial concept                                         (harald)

"""
    tradfri/tradfriActions.py - controlling the Ikea tradfri smart lights

    This module requires libcoap with dTLS compiled, at this moment there is no python coap module
    that supports coap with dTLS. see ../bin/README how to compile libcoap with dTLS support
"""

# pylint convention disablement:
# C0103 -> invalid-name
# pylint: disable=C0103

import sys
import os

global coap
coap = '/usr/local/bin/coap-client'

def tradfri_power_light(hubip, user, userkey, deviceid, value):
    """ function for power on/off tradfri lightbulb """
    tradfriHub = 'coaps://{}:5684/15001/{}' .format(hubip, deviceid)

    if value == 'on':
        payload = '{ "3311": [{ "5850": 1 }] }'
    else:
        payload = '{ "3311": [{ "5850": 0 }] }'

    api = '{} -m put -u "{}" -k "{}" -e \'{}\' "{}"' .format(coap, user, userkey, payload, tradfriHub)

    if os.path.exists(coap):
        os.popen(api)
    else:
        sys.stderr.write('[-] libcoap: could not find libcoap\n')
        sys.exit(1)

    return True


def tradfri_dim_light(hubip, user, userkey, deviceid, value):
    """ function for dimming tradfri lightbulb """
    dim = float(value) * 2.55
    tradfriHub = 'coaps://{}:5684/15001/{}'.format(hubip, deviceid)
    payload = '{ "3311" : [{ "5851" : %s, "5712": 10 }] }' % int(dim)

    api = '{} -m put -u "{}" -k "{}" -e \'{}\' "{}"'.format(coap, user, userkey, payload, tradfriHub)

    if os.path.exists(coap):
        result = os.popen(api)
    else:
        sys.stderr.write('[-] libcoap: could not find libcoap\n')
        sys.exit(1)

    return result

def tradfri_color_light(hubip, user, userkey, deviceid, value):
    """ function for color temperature tradfri lightbulb """
    tradfriHub = 'coaps://{}:5684/15001/{}'.format(hubip, deviceid)

    if value == 'warm':
        payload = '{ "3311" : [{ "5709" : %s, "5710": %s }] }' % ("33135", "27211")
    elif value == 'normal':
        payload = '{ "3311" : [{ "5709" : %s, "5710": %s }] }' % ("30140", "26909")
    elif value == 'cold':
        payload = '{ "3311" : [{ "5709" : %s, "5710": %s }] }' % ("24930", "24684")

    api = '{} -m put -u "{}" -k "{}" -e \'{}\' "{}"'.format(coap, user, userkey, payload, tradfriHub)

    if os.path.exists(coap):
        result = os.popen(api)
    else:
        sys.stderr.write('[-] libcoap: could not find libcoap\n')
        sys.exit(1)

    return result

def tradfri_color_percent(hubip, user, userkey, deviceid, value):
    """ function for color temperature tradfri lightbulb """
    tradfriHub = 'coaps://{}:5684/15001/{}'.format(hubip, deviceid)
    pc = int(value)

    if not (0 <= pc <= 100):
        sys.stderr.write("Don't understand colour temp")
        return -1
    
    tempx = int(24930 + (82.05 * pc))  # 24930 - 33135
    tempy = (24694 + (25.17 * (100 - pc))) # 24694 - 27211
    
    payload = '{ "3311" : [{ "5709" : %s, "5710": %s, "5712": 10 }] }' % (int(tempx), int(tempy))
    
    sys.stderr.write("Send payload %s" % payload)

    api = '{} -m put -u "{}" -k "{}" -e \'{}\' "{}"'.format(coap, user, userkey, payload, tradfriHub)

    if os.path.exists(coap):
        result = os.popen(api)
    else:
        sys.stderr.write('[-] libcoap: could not find libcoap\n')
        sys.exit(1)

    return result

def tradfri_power_group(hubip, user, userkey, groupid, value):
    """ function for power on/off tradfri lightbulb """
    tradfriHub = 'coaps://{}:5684/15004/{}' .format(hubip, groupid)

    if value == 'on':
        payload = '{ "5850" : 1 }'
    else:
        payload = '{ "5850" : 0 }'

    api = '{} -m put -u "{}" -k "{}" -e \'{}\' "{}"' .format(coap, user, userkey,
                                                                          payload, tradfriHub)

    if os.path.exists(coap):
        result = os.popen(api)
    else:
        sys.stderr.write('[-] libcoap: could not find libcoap\n')
        sys.exit(1)

    return result


def tradfri_dim_group(hubip, user, userkey, groupid, value):
    """ function for dimming tradfri lightbulb """
    tradfriHub = 'coaps://{}:5684/15004/{}'.format(hubip, groupid)
    dim = float(value) * 2.55
    payload = '{ "5851" : %s }' % int(dim)

    api = '{} -m put -u "{}" -k "{}" -e \'{}\' "{}"'.format(coap, user, userkey,
                                                                         payload, tradfriHub)

    if os.path.exists(coap):
        result = os.popen(api)
    else:
        sys.stderr.write('[-] libcoap: could not find libcoap\n')
        sys.exit(1)

    return result
