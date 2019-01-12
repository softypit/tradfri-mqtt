#!/bin/sh

start() {
    python /usr/bin/tradfri/tradfri_mqtt.py 192.168.1.110 Paul tspKRgpwwWIwozbS 192.168.1.229 1883 &
    mypid = $!
    echo -n $mypid > /var/tradfri_mqtt_pid
}

stop() {
    [ -e /var/tradfri_mqtt_pid ] && {
        mypid = $(cat /var/tradfri_mqtt_pid)
        kill $mypid
	rm /var/tradfri_mqtt_pid
    }
}

case $1 in 
  start|stop) "$1" ;;
esac

