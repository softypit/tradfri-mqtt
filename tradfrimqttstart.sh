#!/bin/sh

start() {
    python /usr/bin/tradfri/tradfri_mqtt.py <tradfri gateway ipaddr here> <username> <key> <mqtt broker url> <mqtt broker port> &
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

