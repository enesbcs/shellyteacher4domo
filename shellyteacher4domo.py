#!/usr/bin/env python3
import re
import time
import json
import urllib
import settings
import paho.mqtt.client as mqtt #pip3 install paho-mqtt
import sys, os

class MQTTClient(mqtt.Client): # Gen1 detailed infos and Gen2 alive
 subscribechannel = ""

 def on_connect(self, client, userdata, flags, rc):
  try:
   self.subscribe(self.subscribechannel,0)
   if settings.debug:
    print("subscribed",self.subscribechannel)#debug
  except Exception as e:
   print("MQTT connection error: "+str(e))
  try:
   rc = int(rc)
  except:
   rc=-1
  if rc !=0:
   estr = str(rc)
   if rc==1:
      estr += " Protocol version error!"
   if rc==3:
      estr += " Server unavailable!"
   if rc==4:
      estr += " User/pass error!"
   if rc==5:
      estr += " Not authorized!"
   print("MQTT connection error: "+estr)

 def on_message(self, mqttc, obj, msg):
   msg2 = msg.payload.decode('utf-8')
   lista = []
   if ('{' in msg2):
    try:
     lista = json.loads(msg2)
    except Exception as e:
     print("JSON decode error:"+str(e)+str(msg2))
     lista = []
   if (lista) and (len(lista)>0):
     if settings.debug:
      print( "on_message::payload::" + str(msg2))
     if "id" in lista: #gen1&gen2
       if lista['id'] not in settings.shque:
        settings.shque.append(lista['id'])
        settings.shjsons[ lista['id'] ] = lista
       else:
        print(lista['id']," alive")

class MQTTClientOnlineCheck(mqtt.Client): #Gen2 hack to get some infos...
 subscribechannel = ""

 def on_connect(self, client, userdata, flags, rc):
  try:
   self.subscribe(self.subscribechannel,0)
   if settings.debug:
    print("subscribed",self.subscribechannel)#debug
  except Exception as e:
   print("MQTT connection error: "+str(e))
  try:
   rc = int(rc)
  except:
   rc=-1
  if rc !=0:
   estr = str(rc)
   if rc==1:
      estr += " Protocol version error!"
   if rc==3:
      estr += " Server unavailable!"
   if rc==4:
      estr += " User/pass error!"
   if rc==5:
      estr += " Not authorized!"
   print("MQTT connection error: "+estr)

 def on_message(self, mqttc, obj, msg):
   try:
    msg2 = msg.payload.decode('utf-8')
    topic = str(msg.topic)
   except:
    msg2 = ""
    topic = ""
   if "true" in msg2:
     t = topic.split("/")
     sid = t[0]
     print("ONLINE GEN2", sid)
     nmsg = { "topic": sid + '/rpc', "payload": '{"id": 1, "src":"shellies_discovery", "method":"Shelly.GetConfig"}' } # force gen2 device to properly identify itself... OMG
     settings.mqttsender.append(nmsg)

def get_shelly(purl): #get infos through http
  st = ""
  sm = ""
  rescode = 0
  try:
   content = urllib.request.urlopen("http://"+purl+"/settings", None, 2)
  except Exception as e:
   rescode = -1
  if rescode == 0:
   try:
    rescode = content.getcode()
   except Exception as e:
    rescode = -1
   if (rescode == 200):
    try:
     retdata = content.read()
    except:
     retdata = ""
    msg2 = retdata.decode('utf-8')
    if ('{' in msg2):
     list = []
     try:
      list = json.loads(msg2)
     except Exception as e:
      print("JSON decode error:",e,"'",msg2,"'")
      list = []
     if (list):
      if 'device' in list:
       if 'type' in list['device']:
        st = str(list['device']['type'])
      if 'fw_mode' in list:
        sm = str(list['fw_mode'])
      elif 'mode' in list:
        sm = str(list['mode'])
  return st, sm

def fill_template_str(template, values): # values = {"shelly_id": "shelly-xxxx", "shelly_mac": "abcdefgh"}
   cline = template
   if "%" in cline:
    m = re.findall(r"\%([A-Za-z0-9_#\+\-]+)\%", cline)
    if len(m)>0: # replace with values
     for r in range(len(m)):
      if m[r].lower() in values:
       cline = cline.replace("%"+m[r]+"%",str(values[m[r]]))
   return cline

class TemplateDataFile:
    f = None
    template = {}
    templatename = ""

    def __init__(self, file_name):
        try:
         self.f = open(file_name, 'r')
        except:
         self.f = None
         print( "ERROR: File open error: " + str(file_name))

        self.template = []
        self.templatename = ""

    def close(self):
        if self.f:
            self.f.close()
            self.f = None

    def opened(self):
        if (self.f is not None):
         try:
          return (self.f.closed == False)
         except:
          pass
        return False

    def get_templates(self,templatename):
        tfs = False
        tfe = False
        self.templatename = ""
        self.template = []
        if self.f is not None:
           self.f.seek(0, 0)
           self.templatename = str(templatename)
           try:
            mt = {}
            while True:
             file_line = self.f.readline()
             if not file_line:
              break
             # Skip the comment lines
             if len( file_line.lstrip()) == 0 or file_line.lstrip()[0] == "#":
               continue
             if tfs==False and tfe==False: #searching model
              if "["+ self.templatename + "]" in file_line:
               tfs = True
             elif tfs and tfe==False: # templatestr's
               if file_line == "" or file_line[0] == "[":
                tfe = True
                break
               file_line = file_line.strip()
               equpos = file_line.find("=")
               if equpos in [5,7]:
                if file_line[:5]=="topic":
                   mt['topic'] = file_line[(equpos+1):].strip()
                elif file_line[:7]=="payload":
                   mt['payload'] = file_line[(equpos+1):].strip()
                   self.template.append(mt)
                   mt = {}
           except Exception as e:
            print(e)
        if tfe is False or len(self.template)<1:
           self.templatename = ""
        return self.template

pathname = os.path.dirname(sys.argv[0])

if settings.testrun==False:
 if settings.gen1:
  mqttclient1 = MQTTClient() #gen1
  mqttclient1.subscribechannel = settings.data['trigger_topic1']
  print("Connecting to MQTT server...")
  loopok = False
  try:
    mqttclient1.connect(settings.data['mqtt_ip'],int(settings.data['mqtt_port']),keepalive=60)
    mqttclient1.loop_start()
    loopok = True
  except Exception as e:
    print("Connection failed to MQTT server at "+str(settings.data['mqtt_ip']),e)
 if settings.gen2:
  mqttclient2 = MQTTClient() #gen2
  mqttclient2.subscribechannel = settings.data['trigger_topic2']
  print("Connecting to MQTT server...")
  loopok = False
  try:
    mqttclient2.connect(settings.data['mqtt_ip'],int(settings.data['mqtt_port']),keepalive=60)
    mqttclient2.loop_start()
    loopok = True
  except Exception as e:
    print("Connection failed!",e)
  mqttclient3 = MQTTClientOnlineCheck() #gen2 online
  mqttclient3.subscribechannel = settings.data['trigger_topic3']
  print("Connecting to MQTT server...")
  loopok = False
  try:
    mqttclient3.connect(settings.data['mqtt_ip'],int(settings.data['mqtt_port']),keepalive=60)
    mqttclient3.loop_start()
    loopok = True
  except Exception as e:
    print("Connection failed!",e)
else:
 print("Test run without mqtt connection")
 loopok = True
 if settings.gen1:
  settings.shque.append("shellymotionsensor-60A42397667E")
  settings.shjsons["shellymotionsensor-60A42397667E"] = {"id":"shellymotionsensor-60A42397667E","model":"SHMOS-01","mac":"60A42397667E","ip":"192.168.2.32","new_fw":False,"fw_ver":"20211026-072015/v2.0.3@1dfb9313"}  

 if settings.gen2:
  settings.shque.append("shellyplus1-a8032abcf5f0")
  settings.shjsons["shellyplus1-a8032abcf5f0"] = {"id":1,"src":"shellyplus1-a8032abcf5f0","dst":"shellies_discovery","result":{"mqtt":{"enable":True,"topic_prefix":"shellyplus1-a8032abcf5f0","rpc_ntf":True,"status_ntf":True,"use_client_cert":False},"sys":{"device":{"name":None,"mac":"A8032ABCF5F0","fw_id":"20221206-141227/0.12.0-gafc2404","discoverable":True,"eco_mode":False,"addon_type":None}}}}

decodinprog = False
if settings.gen1:
 filename = os.path.join( str(pathname) , settings.data['gen1_template_file'] )
 tf = TemplateDataFile( filename ) # init template database file for Gen1 devices
if settings.gen2:
 filename = os.path.join( str(pathname) , settings.data['gen2_template_file'] )
 tf2 = TemplateDataFile( filename ) # init template database file for Gen2 devices

print("Starting eval loop, waiting Shelly devices to appear on MQTT announce... press CTRL-C to cancel")
while loopok:
 if len(settings.shque)>0 and decodinprog==False: #processing incoming messages
  decodinprog = True
  devid = settings.shque[0]
  suc = False
  if devid in settings.shjsons:
    if ('src' in settings.shjsons[devid]) and ('result' in settings.shjsons[devid]):
      guessmodel = settings.shjsons[devid]['src'] #Gen2 device!
      model = guessmodel.split("-")
      di = {"shelly_id": settings.shjsons[devid]['src'], "shelly_topic": settings.shjsons[devid]['result']['mqtt']['topic_prefix'], "shelly_model": model[0],"shelly_mac":  settings.shjsons[devid]['result']['sys']['device']['mac'],"shelly_ip": "", "shelly_mode": "", "discovery_prefix": settings.data['discovery_prefix']}     
      mt = tf2.get_templates(model[0])      # get template for specific model
      if len(mt)>0:
         print(">>>GEN2 device ",di["shelly_id"],di["shelly_topic"],"found")

         for i in range(len(mt)):
            mqttstr = {"topic": fill_template_str(mt[i]['topic'], di),"payload": fill_template_str(mt[i]['payload'], di)}
            settings.mqttsender.append(mqttstr)
      else:
         print("---ERROR: GEN2 device ",di["shelly_id"],di["shelly_topic"],"template not found")

    else:
     devinfo = settings.shjsons[devid] # get next Gen1 device from queue
     try: # fallback id
      if ('model' not in devinfo or devinfo['model'] == "") or ('mode' not in devinfo or devinfo['mode'] == ""):
       model, mode = get_shelly(devinfo["ip"])
       if 'model' not in devinfo:
          devinfo.update({'model': ''})
       if 'mode' not in devinfo:
          devinfo.update({'mode': ''})
       if model != "" and devinfo['model'] == "":
        devinfo['model'] = model
       if mode != "" and devinfo['mode'] == "":
        devinfo['mode'] = mode
     except Exception as e:
      pass
     if 'model' in devinfo and devinfo['model'] != "":
      di = {"shelly_id": devinfo['id'], "shelly_model": devinfo['model'],"shelly_mac": devinfo['mac'],"shelly_ip": devinfo['ip'], "shelly_mode": "", "discovery_prefix": settings.data['discovery_prefix']}
      if 'mode' in devinfo:
         di["shelly_mode"] = devinfo["mode"]
      model = di["shelly_model"]
      if di["shelly_mode"] != "":
         model += "-"+di["shelly_mode"]
      mt = tf.get_templates(model)      # get template for specific model

      if len(mt)>0:
         print(">>>GEN1 device ",di["shelly_ip"],di["shelly_model"],di["shelly_id"],"found")

         for i in range(len(mt)):
            mqttstr = {"topic": fill_template_str(mt[i]['topic'], di),"payload": fill_template_str(mt[i]['payload'], di)}
            settings.mqttsender.append(mqttstr)
      else:
         print("---ERROR: GEN1 device ",di["shelly_ip"],di["shelly_model"],di["shelly_id"],"template not found")

  try:
    del settings.shque[0]
  except:
    pass
  try:
    del settings.shjsons[devid]
  except:
    pass
  decodinprog = False
 elif len(settings.mqttsender)>0: #sending out prepared device autoconfig
  mres = 1
  try:
   mres = 0
   if settings.testrun:
    print(settings.mqttsender[0]['topic'],settings.mqttsender[0]['payload']) # debug, only print MQTT
   else:
    t = settings.mqttsender[0]['topic']
    if settings.data['discovery_prefix'] in t:
       ret = settings.retain
    else:
       ret = False # retain not needed if it is not discovery configuration
    (mres,mid) = mqttclient1.publish(settings.mqttsender[0]['topic'],settings.mqttsender[0]['payload'],retain=ret)
  except:
   mres = 1
  if mres==0:
   try:
    del settings.mqttsender[0]
   except:
    pass
 else:
  time.sleep(0.1)
