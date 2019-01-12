# tradfri_mqtt

python daemon to enable control of tradfri smartlights using mqtt. 
Lamps/groups can be switched on/off, dimmed, and have colour temperature adjusted.
Current state of lamps/groups is published when they change.

### requirements

this is derived from ikea-smartlight by hvanderlaan and has the same requirements of libcoap with dTLS. This will likely require a rebuild of libcoap from source.
there is no requirement for tqdm

### what it does

tradfri_mqtt is started with arguments of ikea gateway url, username, password, mqtt gateway url and mqtt port

Most docs I have seen show using the Client_identity username with the key printed on the gateway to send coap commands. On my unit this did not work. I could only use the 
Client_identity credentials to create a new user account so tradfri_mqtt requires a user/key to be supplied to authenticate with the gateway. To create a new account use 
coap-client -m post -u "Client_identity" -v 5 -k "<default key>" -e '{"9090":"<username>"}' "coaps://<gateway ip>//15011/9063". The response contains the key
e.g. response: {"9091":"<new key here>","9029":"1.4.0015"}. The new user account could then be used to control tradfri devices.

All devices on the gateway are members of groups so discovery occurs by reading all groups and then looking for devices within those groups. Groups and devices discovered
are published to tradfri/bulblist and tradfri/grouplist as json e.g. {"bulbs":[{"id":"xxx", "name":"xxx"},{"id":"xxx", "name":"xxx"}]}

tradfri_mqtt addresses bulbs and groups by ID and name. The name is the one defined in the tradfri smartphone app when setting up the devices

tradfri_mqtt continually polls all devices for state changes and publishes any changes to tradfri/lightstatus/<id>/xxx, tradfri/lightstatus/<name>/xxx
for every change the device name/id and group name/id topics will be published to keep interested applications up to date. This allows for home automation
applications to know the device state even if it was changed with the tradfri app.

when polling groups the current state of all bulbs is not always reflected so bulbs are polled individually and a group status is collated


bulbs and groups can have on/off and brightness set and some bulbs will support colour temperature

to set a bulb/group parameter:

brightness:
publish <percent> to tradfri/setlight/<id/name>/brightness

power:
publish 'on' or 'off' to tradfri/setlight/<id/name>/power

colour temperature:
publish <percent warm white> to tradfri/setlight/<id/name>/temp

