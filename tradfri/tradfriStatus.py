#!/usr/bin/env python

# file        : tradfri/tradfriStatus.py
# purpose     : getting status from the Ikea tradfri smart lights
#
# author      : harald van der laan
# date        : 2017/04/10
# version     : v1.1.0
#
# changelog   :
# - v1.1.0      refactor for cleaner code                               (harald)
# - v1.0.0      initial concept                                         (harald)

"""
    tradfriStatus.py - module for getting status of the Ikea tradfri smart lights

    This module requires libcoap with dTLS compiled, at this moment there is no python coap module
    that supports coap with dTLS. see ../bin/README how to compile libcoap with dTLS support
"""

# pylint convention disablement:
# C0103 -> invalid-name
# pylint: disable=C0103

import sys
import os
import json

global coap
coap = '/usr/local/bin/coap-client'

def tradfri_get_devices(hubip, name, securityid):
    """ function for getting all tradfri device ids """
    tradfriHub = 'coaps://{}:5684/15001' .format(hubip)
    api = '{} -m get -B 30 -u "{}" -k "{}" "{}" | awk \'NR==4\'' .format(coap, name, securityid, tradfriHub)

    if os.path.exists(coap):
        result = os.popen(api)
    else:
        sys.stderr.write('[-] libcoap: could not find libcoap.\n')
        sys.exit(1)
    response = result.read()
    try:
        report = json.loads(result.read().strip('\n'))
    except Exception as e:
        print("Failed to decode devices {} - response was {}".format(e, response))
        report = ""
    return report

def tradfri_get_lightbulb(hubip, name, securityid, deviceid):
    """ function for getting tradfri lightbulb information """
    tradfriHub = 'coaps://{}:5684/15001/{}' .format(hubip, deviceid)
    api = '{} -m get -B 30 -u "{}" -k "{}" "{}" | awk \'NR==4\''.format(coap, name, securityid, tradfriHub)

    if os.path.exists(coap):
        result = os.popen(api)
    else:
        sys.stderr.write('[-] libcoap: could not find libcoap.\n')
        sys.exit(1)
    response = result.read()
    try:
        report = json.loads(response.strip('\n'))
    except Exception as e:
        print("Failed to decode bulb status {} - response was {}".format(e, response))
        report = ""
    return report

def tradfri_get_groups(hubip, name, securityid):
    """ function for getting tradfri groups """
    tradfriHub = 'coaps://{}:5684/15004'.format(hubip)
    api = '{} -m get -B 30 -u "{}" -k "{}" "{}" | awk \'NR==4\''.format(coap, name, securityid, tradfriHub)

    if os.path.exists(coap):
        result = os.popen(api)
    else:
        sys.stderr.write('[-] libcoap: could not find libcoap.\n')
        sys.exit(1)
    response = result.read()
    try:
        report = json.loads(response.strip('\n'))
    except Exception as e:
        print("Failed to decode groups {} - response was {}".format(e, response))
        report = ""
    return report

def tradfri_get_group(hubip, name, securityid, groupid):
    """ function for getting tradfri group information """
    tradfriHub = 'coaps://{}:5684/15004/{}'.format(hubip, groupid)
    api = '{} -m get -B 30 -u "{}" -k "{}" "{}" | awk \'NR==4\''.format(coap, name, securityid, tradfriHub)

    if os.path.exists(coap):
        result = os.popen(api)
    else:
        sys.stderr.write('[-] libcoap: could not find libcoap.\n')
        sys.exit(1)

    response = result.read()
    try:
        report = json.loads(response.strip('\n'))
    except Exception as e:
        print("Failed to decode group status {} - reponse was {}".format(e, response))
        report = ""
    return report
