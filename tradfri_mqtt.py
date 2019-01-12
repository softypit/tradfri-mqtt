import sys
import paho.mqtt.client as mqtt
import time
import threading
from threading import Lock
import array as arr
from tradfri import tradfriActions
from tradfri import tradfriStatus
#import ConfigParser

class tradfridevice:
    def __init__(self):
        self.id = ""
        self.name = ""
        self.active = ""
        self.power = ""
        self.brightness = ""
        self.colour = ""
        self.isspectrum = False
        self.isrgb = False
    

class tradfrigroup:
    def __init__(self):
        self.id = ""
        self.name = ""
        self.active = ""
        self.power = ""
        self.brightness = ""
        self.devices = []
        
    def find_device(dev):
        print("Find device")
        if self.devices != []:
            print("Got devices")
            for dvc in self.devices:
                print("Check dev {}".format(dvc.id))
                if dev.isnumeric():
                    if int(dvc.id) == int(dev):
                        return dvc
                else:
                    if dvc.name == dev:
                        return dvc
        return None

gatewayurl = format(sys.argv[1])
username = format(sys.argv[2])
userkey = format(sys.argv[3])
mqttBrokerURL = format(sys.argv[4])
mqttBrokerPort = format(sys.argv[5])

mutex = threading.Lock()


    

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("tradfri/setlight/#", 0)
    
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))
    
    topicelem = msg.topic.split("/")
    # Make sure there are at least 4 elements in the topic string
    devaddr = topicelem[2]
    
    print "devaddr is {}".format(devaddr)
    if devaddr == "update_devices":
        read_devices()
        return
    
    cmd = topicelem[3]
    
    group = False
    #print("Devaddr is {}".format(devaddr))
    ep = match_endpoint(groups, devaddr)
    
    # endpoint could be a group or individual device - we treat them differently
    if isinstance(ep, tradfrigroup):
        group = True
    
    if cmd == "brightness":
        print("Set {} - {} brightness to {}".format(ep.name, ep.id, msg.payload))
        #print("Brightness get mutex")
        mutex.acquire()
        if msg.payload.lower() == 'on' or msg.payload.lower() == 'off':
            if group == False:
                tradfriActions.tradfri_power_light(gatewayurl, username, userkey, ep.id, msg.payload.lower())
            else:
                tradfriActions.tradfri_power_group(gatewayurl, username, userkey, ep.id, msg.payload.lower())
        else:
            try:
                if 0 <= int(msg.payload) <= 100:
                    if 0 == int(msg.payload):
                        if group == False:
                            tradfriActions.tradfri_power_light(gatewayurl, username, userkey, ep.id, "off")
                        else:
                            tradfriActions.tradfri_power_group(gatewayurl, username, userkey, ep.id, "off")
                    else:
                        if group == False:
                            tradfriActions.tradfri_dim_light(gatewayurl, username, userkey, ep.id, msg.payload)
                        else:
                            tradfriActions.tradfri_dim_group(gatewayurl, username, userkey, ep.id, msg.payload)
                else:
                    sys.stderr.write('Tradfri: dim value can only be between 0 and 100\n')
            except:
                sys.stderr.write('unable to decode dimmer value {}\n'.format(msg.payload))
                pass
        mutex.release()
        #print("Brightness release mutex")
        #cmdready.set()
    if cmd == "power":
        print("Set {} power {}".format(ep.name, msg.payload))
        #print("Power get mutex")
        mutex.acquire()
        if msg.payload.lower() == 'on' or msg.payload.lower() == 'off':
            if group == False:
                tradfriActions.tradfri_power_light(gatewayurl, username, userkey, ep.id, msg.payload.lower())
            else:
                tradfriActions.tradfri_power_group(gatewayurl, username, userkey, ep.id, msg.payload.lower())
        else:
            sys.stderr.write('Tradfri: power state can only be on/off\n')
        mutex.release()
        #print("Power release mutex")
        #cmdready.set()
    if cmd == "temp":
        # if this is a group id we need to set the temp on individual bulbs as they can't be set as a group
        print("Set {} colour temperature {}% warm".format(ep.name, msg.payload))
        #print("Temp get mutex")
        mutex.acquire()
        try:
            if 0 <= int(msg.payload) <= 100:
                if group == True:
                    for bulb in ep.devices:
                        if bulb.isspectrum == True:
                            tradfriActions.tradfri_color_percent(gatewayurl, username, userkey, bulb.id, msg.payload)
                else:
                    tradfriActions.tradfri_color_percent(gatewayurl, username, userkey, ep.id, msg.payload)
            else:
                sys.stderr.write('Tradfri: colour value can only be between 0 and 100\n')
        except:
            sys.stderr.write('unable to decode colour value {}\n'.format(msg.payload))
        mutex.release()
        #print("Temp release mutex") 
        #cmdready.set()
    if cmd == "poll":
        cmdready.set()


#def get_devices(devlist):
#    for thisdev in devlist:
#        bulbstat = tradfriStatus.tradfri_get_lightbulb(gatewayurl, username, userkey, thisdev.id)
#        if bulbstat != "":
#            onoff = "OFF"
#            power = "OFF"
#            if bulbstat["3311"][0]["5850"] == 1:
#                onoff = "ON"
#            if bulbstat["9019"] == 1:
#                power = "ON"
#            print('Got bulb - ID: {}, name: {}, power {}, brightness: {}, state: {}'.format(bulbstat["9003"], bulbstat["9001"], power, bulbstat["3311"][0]["5851"], onoff))
#            thisdev.name = bulbstat["9001"]
#            thisdev.active = power
#            thisdev.power = onoff
#            bright = bulbstat["3311"][0]["5851"]
#            bright = (bright / 255) * 100
#            thisdev.brightness = "{}".format(int(bright))
#            thisdev.colour = 0
        
    
def get_groups(grouplist):
    firstgroup = True
    firstbulb = True
    bulbreport = "{\"bulbs\":["
    groupreport = "{\"groups\":["
    for thisgroup in grouplist:
        groupstat = tradfriStatus.tradfri_get_group(gatewayurl, username, userkey, thisgroup.id)
        if groupstat != "":
            gpow = "OFF"
            
            thisgroup.name = groupstat["9001"]
            print("Read group {}".format(thisgroup.name))
            if int(groupstat["5850"]) > 0:
                thisgroup.power = "ON"
            else:
                thisgroup.power = "OFF"
            bright = groupstat["5851"]
            bright = (bright / 255) * 100 
            thisgroup.brightness = "{}".format(int(bright))
            if firstgroup is False:
                groupreport += ","
            firstgroup = False
            groupreport += "{{\"id\":\"{}\",\"name\":\"{}\"}}".format(thisgroup.id, thisgroup.name)
            devl = groupstat["9018"]["15002"]["9003"]
            for dev in devl:
                bulbstat = tradfriStatus.tradfri_get_lightbulb(gatewayurl, username, userkey, dev)
                onoff = "OFF"
                power = "OFF"
                try:
                    if bulbstat["3311"][0]["5850"] == 1:
                        onoff = "ON"
                    if bulbstat["9019"] == 1:
                        power = "ON"
                        gpower = "ON"
                except KeyError:
                    # device is not a lightbulb but a remote control, dimmer or sensor
                    continue
                print('Got bulb - ID: {}, name: {}, power {}, brightness: {}, state: {}'.format(bulbstat["9003"], bulbstat["9001"], power, bulbstat["3311"][0]["5851"], onoff))
                newdevice = tradfridevice()
                newdevice.id = bulbstat["9003"]
                newdevice.name = bulbstat["9001"]
                newdevice.power = onoff
                bright = bulbstat["3311"][0]["5851"]
                bright = (bright / 255) * 100 
                newdevice.brightness = "{}".format(int(bright))
                
                try:
                    valx = bulbstat["3311"][0]["5709"]
                    #valy = bulbstat["3311"][0]["5710"]
                    newdevice.isspectrum = True
                    valx -= 24930
                    #valy -= 24694
                    pc = valx / 82.05
                    newdevice.colour = int(pc)
                    print("Spectrum bulb temp {}%".format(newdevice.colour))
                except KeyError:    
                    newdevice.colour = 0
                    print("Not a spectrum bulb")
                    pass

                newdevice.rgb = False
                # no power reported for group so we derive from ANY of the bulbs
                thisgroup.active = gpower
                thisgroup.devices.append(newdevice)
                if firstbulb is False:
                    bulbreport += ","
                firstbulb = False
                bulbreport += '{{"id":"{}","name":"{}"}}'.format(newdevice.id, newdevice.name)
    groupreport += "]}"
    bulbreport += "]}"
    print("Publish bulblist - {}".format(bulbreport))
    client.publish("tradfri/bulblist", bulbreport, 0)
    print("Publish grouplist - {}".format(groupreport))
    client.publish("tradfri/grouplist", groupreport, 0)

def group_find_device(group, dev):
    if group.devices != []:
        for dvc in group.devices:
            #print("Check dev {}".format(dvc.id))
            if dev.isnumeric():
                if int(dvc.id) == int(dev):
                    return dvc
            else:
                if dvc.name == dev:
                    return dvc
                
    return None
        
def groups_find_device(grouplist, dev):
    for grp in grouplist:
        dvc = group_find_device(grp, dev)
        #dvc = grp.find_device(dev)
        if dvc is not None:
            #print("Found device {}".format(dvc.name))
            return dvc
    return None

# Given a name find a group or individual bulb 
def match_endpoint(grouplist, epid):
    for grp in grouplist:
        # Yuck - sort this mess out
        #print("Check group {}".format(grp.name))
        if epid.isnumeric():
            #print("Group endpoint is numeric {}".format(grp.id))
            if int(epid) == int(grp.id):
                #print("Found group {}".format(grp.name))
                return grp
        elif epid == grp.name:
            #print("Found group {}".format(grp.name))
            return grp
    # Failed to match a group - search for a bulb
    return groups_find_device(grouplist, epid)

#devices = []
groups = []

def read_devices():
    del groups[:]
    grouplist = tradfriStatus.tradfri_get_groups(gatewayurl, username, userkey)
    for groupid in grouplist:
        newgroup = tradfrigroup()
        newgroup.id = groupid            
        groups.append(newgroup)
    get_groups(groups)


if __name__ == '__main__':

    #conf = ConfigParser.ConfigParser()
    #conf.read('tradfri.cfg')

    #hubip = conf.get('tradfri', 'hubip')
    #securityid = conf.get('tradfri', 'securityid')
    #user = conf.get('tradfri', 'username')
    #userkey = conf.get('tradfri', 'userkey')
    
    cmdready = threading.Event()
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect_async(mqttBrokerURL, mqttBrokerPort, 60)
    client.loop_start()
    
    #grouplist = tradfriStatus.tradfri_get_groups(gatewayurl, username, userkey)
    #for groupid in grouplist:
    #    newgroup = tradfrigroup()
    #    newgroup.id = groupid            
    #    groups.append(newgroup)
       
    ##get_devices(devices)
    #get_groups(groups)

    read_devices()
    
    sendall = True

    while True:
         
        cmdready.wait(10)
        cmdready.clear()
        
        for thisgroup in groups:
            gonoff = "OFF"
            gpow = "OFF"
            gbrightness = 0
            gnumdevs = 0
            
            if thisgroup.devices is not None:
                for thisdev in thisgroup.devices:
            
                    onoff = "OFF"
                    power = "OFF"
                    #print("Main get mutex")
                    mutex.acquire()
                    bulbstat = tradfriStatus.tradfri_get_lightbulb(gatewayurl, username, userkey, thisdev.id)
                    mutex.release()
                    #print("Main release mutex")
                    #print('bulbstat is {}',format(bulbstat))
                    if bulbstat != "":
                        try:
                            if bulbstat["3311"][0]["5850"] == 1:
                                onoff = "ON"
                            if bulbstat["9019"] == 1:
                                power = "ON"
                            bright = float(bulbstat["3311"][0]["5851"])
                            
                        except KeyError:
                            # Problem with the returned json - skip
                            print("Error polling bulb {}:{}".format(thisdev.name, thisdev.id))
                            continue
                        
                        if power != thisdev.active or sendall is True:
                            thisdev.active = power
                            client.publish("tradfri/lightstatus/{}/power".format(thisdev.id), power, 0)
                            client.publish("tradfri/lightstatus/{}/power".format(thisdev.name), power, 0)
                        if onoff != thisdev.power or sendall is True:
                            thisdev.power = onoff                       
                            client.publish("tradfri/lightstatus/{}/lamp".format(thisdev.id), onoff, 0)
                            client.publish("tradfri/lightstatus/{}/lamp".format(thisdev.name), onoff, 0)
                        bright = (bright / 255) * 100
                        brightstr = "{}".format(int(bright))
                        if brightstr != thisdev.brightness or sendall is True:
                            thisdev.brightness = brightstr
                            client.publish("tradfri/lightstatus/{}/brightness".format(thisdev.id), brightstr, 0)
                            client.publish("tradfri/lightstatus/{}/brightness".format(thisdev.name), brightstr, 0)
                        print('bulb ID {}, name: {}, power {}, brightness: {}, state: {}'.format(thisdev.id, thisdev.name, power, brightstr, onoff))
                        
                        if thisdev.isspectrum is True:
                            try:
                                valx = bulbstat["3311"][0]["5709"]
                                #valy = bulbstat["3311"][0]["5710"]
                                valx -= 24930
                                #valy -= 24694
                                pc = valx / 82.05
                                currcolour = int(pc)
                                print("Colour temp is {}%".format(currcolour))
                                if currcolour != thisdev.colour or sendall is True:
                                    client.publish("tradfri/lightstatus/{}/temp".format(thisdev.id), str(currcolour), 0)
                                    client.publish("tradfri/lightstatus/{}/temp".format(thisdev.name), str(currcolour), 0)
                                    thisdev.colour = currcolour
                            except KeyError:
                                print("Can't get colour temperature for {}".format(thisdev.id))
                                pass
                                    
                        if onoff == "ON":
                            gonoff = "ON"
                        if power == "ON":
                            gpow = "ON"
                        gbrightness += int(bright)
                        gnumdevs += 1
                            
                    else:
                        print("Unable to get bulb state for {}:{}".format(thisdev.name, thisdev.id))
                        print("Pause tradfri polling for 30 seconds")
                        cmdready.wait(30)
                        cmdready.clear()
                        
            # We can read the power/brightness from the group but this doesn't reflect the 'live' state of the bulbs 
            # if they've been changed directly
            # We can also create a composite brightness using the state of each of the bulbs but this doesn't always update
            # if the bulbs were set as a group
            # So we need to compromise and use the group data for the group and ignore the individual bulb status which was
            # reported for each device previously
            # We do however assume any powered bulbs from the group device list means the group is on.
            
            # So remember: 
            # the group status is only valid if the bulbs were set as a group
            # likewise the individual bulb status is only valid if the bulbs were set individually
            
            # To read on/bright for group use this bit:    
            #mutex.acquire()
            #groupstat = tradfriStatus.tradfri_get_group(gatewayurl, username, userkey, thisgroup.id)
            #mutex.release()
            #try:
            #    if int(groupstat["5850"]) > 0:
            #        gonoff = "ON"
            #    else:
            #        gonoff = "OFF"
            #    bright = float(groupstat["5851"])
            #    bright = (bright / 255) * 100 
            #    brightstr = "{}".format(int(bright))
            
                # To collate status from the individual bulbs use this bit:
                # collate the group data - brightness is total % values divided by the number of bulbs
                # assume the group is on if ANY of the bulbs are on (they SHOULD be consistent)
            
                if gnumdevs > 0:
                    brightav = gbrightness / gnumdevs
                else:
                    # This is impossible - but just in case .....
                    brightav = gbrightness
                brightstr = "{}".format(int(brightav))
            
                # We can only get active status from the bulbs (it doesn't propagate out to the group)
                if gpow != thisgroup.active or sendall is True:
                    thisgroup.active = gpow
                    client.publish("tradfri/lightstatus/{}/power".format(thisgroup.id), gpow, 0)
                    client.publish("tradfri/lightstatus/{}/power".format(thisgroup.name), gpow, 0)
                if gonoff != thisgroup.power or sendall is True:
                    thisgroup.power = gonoff
                    client.publish("tradfri/lightstatus/{}/lamp".format(thisgroup.id), gonoff, 0)
                    client.publish("tradfri/lightstatus/{}/lamp".format(thisgroup.name), gonoff, 0)
                
                if brightstr != thisgroup.brightness or sendall is True:
                    thisgroup.brightness = brightstr
                    client.publish("tradfri/lightstatus/{}/brightness".format(thisgroup.id), brightstr, 0)
                    client.publish("tradfri/lightstatus/{}/brightness".format(thisgroup.name), brightstr, 0)
                print('group ID {}, name: {}, brightness: {}, state: {}'.format(thisgroup.id, thisgroup.name, brightstr, gonoff))
            #except:
            #    print("Failed to read group {}".format(thisgroup.name))
            #    print("Pause tradfri polling for 30 seconds")
            #    cmdready.wait(30)
            #    cmdready.clear()
            
        sendall = False
