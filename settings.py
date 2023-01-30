data = { }

data['mqtt_ip'] = '192.168.1.2' # mqtt server ip
data['mqtt_port'] = 1883        # mqtt server port
data['discovery_prefix'] = 'homeassistant' # autodiscovery prefix for Domoticz

data['trigger_topic1'] = "shellies/announce"      #gen1 device detection
data['trigger_topic2'] = "shellies_discovery/rpc" #gen2 device reply
data['trigger_topic3'] = "+/online"               #gen2 device detection

testrun = False
retain  = True
gen1 = True
gen2 = True

shque = []
shjsons = {}
mqttsender = []
