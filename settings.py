data = { }
# -----------------------------------------------
# WARNING: If .ini file exists it will overwrite the default values below!
# -----------------------------------------------
data['mqtt_ip'] = '192.168.1.2' # mqtt server ip
data['mqtt_port'] = 1883        # mqtt server port
data['mqtt_user'] = "mqtt"          # mqtt server username
data['mqtt_pass'] = "user"          # mqtt server password
data['discovery_prefix'] = 'homeassistant' # autodiscovery prefix for Domoticz
testrun = False
retain  = True   # if retain is True, config template will be saved onto mqtt broker permanently
gen1    = True  # enable Gen1 device detection
gen2    = True   # enable Gen2 device detection
debug   = True   # print debug messages if True
# -----------------------------------------------
# DO NOT MODIFY LINES BELOW, UNLESS YOU ARE ABSOLUTELY SURE WHAT YOU ARE DOING!
# -----------------------------------------------
data['trigger_topic1'] = "shellies/announce"      #gen1 device detection
data['trigger_topic2'] = "shellies_discovery/rpc" #gen2 device reply
data['trigger_topic3'] = "+/online"               #gen2 device detection
data['trigger_topic4'] = "shellies/+/online"      #gen2 device detection
data['gen1_template_file'] = 'mqtt_templates.txt'
data['gen2_template_file'] = 'mqtt_templates_gen2.txt'
# -----------------------------------------------
## SYSTEM VARIABLES, DO NOT TOUCH!
# -----------------------------------------------
shque = []
shjsons = {}
mqttsender = []
