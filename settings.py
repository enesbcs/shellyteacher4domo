data = { }

data['mqtt_ip'] = '192.168.1.2' # mqtt server ip
data['mqtt_port'] = 1883        # mqtt server port
data['mqtt_user'] = ""          # mqtt server username
data['mqtt_pass'] = ""          # mqtt server password
data['discovery_prefix'] = 'homeassistant' # autodiscovery prefix for Domoticz

data['trigger_topic1'] = "shellies/announce"      #gen1 device detection
data['trigger_topic2'] = "shellies_discovery/rpc" #gen2 device reply
data['trigger_topic3'] = "+/online"               #gen2 device detection

data['gen1_template_file'] = 'mqtt_templates.txt'
data['gen2_template_file'] = 'mqtt_templates_gen2.txt'

retain  = True   # if retain is True, config template will be saved onto mqtt broker permanently
gen1    = True   # enable Gen1 device detection
gen2    = True   # enable Gen2 device detection

testrun = False  # enable this option only for Debugging!
debug   = False   # print debug messages if True

shque = []
shjsons = {}
mqttsender = []
