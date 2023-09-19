#!/usr/bin/env python3
import settings
import configparser
import sys, os
import re
import time
import json
import urllib
try:
 import paho.mqtt.client as mqtt #pip3 install paho-mqtt
 _mqttok = 1
except Exception as e:
 print("MQTT import error: "+str(e)+"\nPlease install paho-mqtt!")
 _mqttok = 0
try:
 import tkinter as tk
 from tkinter import scrolledtext, Frame, Entry, Checkbutton, Button, IntVar, StringVar
 _tkok = 1
except:
 _tkok = 0 # apt install python3-tk
 app = None

loopok          = True
startprovision   = False
text_area        = None
mqttclient1      = None
pressedsave      = False
guiautoprovision = False

def exitApp():
    global app, loopok
    loopok = False
    app.destroy()

def printLn(s):
    global app, text_area
    if app is not None and text_area is not None:
     try:
      text_area.configure(state ='normal')
      text_area.insert(tk.INSERT,str(s)+"\n")
      text_area.configure(state ='disabled')
      text_area.see('end')
     except:
      print(s)
    else:
     print(s)

def saveSettings():
    global cfg, dbfilename, app, pressedsave
    if pressedsave==False:
       pressedsave=True
    if cfg is not None and app is not None:
     printLn("Saving settings to ini file")
     if cfg.has_section("CONFIG")==False:
      cfg.add_section("CONFIG")
     opts = ['mqtt_ip','mqtt_port','mqtt_user','mqtt_pass','discovery_prefix','testrun','retain','gen1','gen2','debug']
     for o in opts:
      try:
       ovar = str(app.getvar(name=o))
      except:
       ovar = None
      if ovar is not None:
       cfg.set('CONFIG',o, ovar)
     with open(dbfilename, 'w') as configfile:
      cfg.write(configfile)

def changeProvision():
    global startprovision, loopok2
    if startprovision:
       startprovision = False
       printLn("\nDetection stopped!\n")
    else:
       if loopok2==False:
          loopok2 = connect_mqtt()
       if loopok2:
        startprovision = True
        printLn("\nDetection started!\n")


class MQTTClient(mqtt.Client): # Gen1 detailed infos and Gen2 alive
 subscribechannel = ""

 def _on_pre_connect(self, dummy1, dummy2):
     pass

 def on_connect(self, client, userdata, flags, rc):
  try:
   self.subscribe(self.subscribechannel,0)
   if settings.debug:
    printLn("subscribed "+str(self.subscribechannel))
  except Exception as e:
   printLn("MQTT connection error: "+str(e))
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
   printLn("MQTT connection error: "+estr)

 def on_message(self, mqttc, obj, msg):
   msg2 = msg.payload.decode('utf-8')
   lista = []
   if ('{' in msg2):
    try:
     lista = json.loads(msg2)
    except Exception as e:
     printLn("JSON decode error:"+str(e)+str(msg2))
     lista = []
   if (lista) and (len(lista)>0):
     if settings.debug:
      printLn( "on_message::payload::" + str(msg2))
     if "id" in lista: #gen1&gen2
       if lista['id'] not in settings.shque:
        settings.shque.append(lista['id'])
        settings.shjsons[ lista['id'] ] = lista
       else:
        printLn(str(lista['id'])+" alive")

class MQTTClientOnlineCheck(mqtt.Client): #Gen2 hack to get some infos...
 subscribechannel = ""

 def _on_pre_connect(self, dummy1, dummy2):
     pass

 def on_connect(self, client, userdata, flags, rc):
  try:
   self.subscribe(self.subscribechannel,0)
   if settings.debug:
    printLn("subscribed "+str(self.subscribechannel))#debug
  except Exception as e:
   printLn("MQTT connection error: "+str(e))
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
   printLn("MQTT connection error: "+estr)

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
     printLn("ONLINE GEN2 "+str(sid))
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
      printLn("JSON decode error: "+str(e)+" "+str(msg2))
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
         printLn( "ERROR: File open error: " + str(file_name))

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
            printLn(str(e))
        if tfe is False or len(self.template)<1:
           self.templatename = ""
        return self.template

pathname = os.path.dirname(sys.argv[0]) #os.path.dirname(__file__)
# init file settings object
try:
      dbfilename = os.path.join(pathname, 'settings.ini')
      cfg = configparser.ConfigParser()
      cfg.optionxform = str
except Exception as e:
      cfg = None
      _setok = 0
      print("INI error",dbfilename,e)

try:
 fp=sys.argv[1]
except:
 fp=""
if len(fp)>1:
   if fp[1].lower()=="c":
    _tkok = 0
    app = None
    print("Console mode requested")
   elif fp[1].lower()=="a":
    guiautoprovision = True

if _tkok == 1:
     try:
             app = tk.Tk()
     except Exception as e:
             app = None
             _tkok =0
             print("TKInter init failed",e)

if cfg is not None: # read settings if ini file exists
     try:
      cfg.read(dbfilename)
      _setok = 1
     except:
      _setok = 0
     if _setok == 1:
        printLn("Ini file exists")
        try:
         if cfg.has_section("CONFIG"):
          opts = ['mqtt_ip','mqtt_port','mqtt_user','mqtt_pass','discovery_prefix']
          for o in opts:
           try:
            ovar = str(cfg['CONFIG'][o])
           except:
            ovar = None
           if ovar is not None:
            try:
             settings.data[o] = ovar
            except Exception as e:
             printLn("INI error:",str(e))
          opts = ['testrun','retain','gen1','gen2','debug'] #booleans
          for o in opts:
           try:
            ovar = (int(cfg['CONFIG'][o]) == 1)
           except:
            ovar = False
           if o==opts[0]:
            settings.testrun = ovar
           elif o==opts[1]:
            settings.retain = ovar
           elif o==opts[2]:
            settings.gen1 = ovar
           elif o==opts[3]:
            settings.gen2 = ovar
           elif o==opts[4]:
            settings.debug = ovar
          printLn("Ini settings loaded")
        except Exception as e:
          printLn("INI error "+str(e))

if loopok and _tkok==1 and app is not None: # build GUI if available
            print("TKInter is available, GUI started. (add /c or -c parameter at startup to fallback console mode)")
            o_mqtt_ip = StringVar(app,name="mqtt_ip")
            o_mqtt_ip.set(settings.data['mqtt_ip'])
            o_mqtt_port = StringVar(app,name="mqtt_port")
            o_mqtt_port.set(settings.data['mqtt_port'])
            o_mqtt_user = StringVar(app,name="mqtt_user")
            o_mqtt_user.set(settings.data['mqtt_user'])
            o_mqtt_pass = StringVar(app,name="mqtt_pass")
            o_mqtt_pass.set(settings.data['mqtt_pass'])
            o_discovery_prefix = StringVar(app,name="discovery_prefix")
            o_discovery_prefix.set(settings.data['discovery_prefix'])
            o_mqtt_retain = IntVar(app,name="retain")
            o_mqtt_retain.set(settings.retain)
            o_testrun = IntVar(app,name="testrun")
            o_testrun.set(settings.testrun)
            o_debug = IntVar(app,name="debug")
            o_debug.set(settings.debug)
            o_gen1 = IntVar(app,name="gen1")
            o_gen1.set(settings.gen1)
            o_gen2 = IntVar(app,name="gen2")
            o_gen2.set(settings.gen2)

            rwin = 1000
            app.geometry(str(rwin)+"x700")
            app.title("ShellyTeacher for Domoticz MQTT AD")
            app.lift()
            app.protocol('WM_DELETE_WINDOW', exitApp)
            oframe = Frame(app,width=rwin)
            aframe = Frame(app,width=rwin)
            oframe.grid(row=0,column=0,sticky = tk.W,pady=5,padx=5)
            aframe.grid(row=1,column=0,sticky = tk.W,pady=5,padx=5)
            app.columnconfigure(0, weight=1)
            tk.Label(oframe, text = "MQTT server IP",font=('Arial', 12)).grid(column = 0, row = 0)
            e_mqtt_ip = tk.Entry(oframe,font=('Arial', 12),width=30,textvariable=o_mqtt_ip)
            e_mqtt_ip.grid(column = 1, row = 0,sticky = tk.W)
            tk.Label(oframe, text = "MQTT port",font=('Arial', 12)).grid(column = 2, row = 0)
            e_mqtt_port = tk.Entry(oframe,font=('Arial', 12),width=5, textvariable=o_mqtt_port)
            e_mqtt_port.grid(column = 3, row = 0,sticky = tk.W)

            tk.Label(oframe, text = "MQTT user",font=('Arial', 12)).grid(column = 0, row = 1)
            e_mqtt_user = tk.Entry(oframe,font=('Arial', 12),width=20, textvariable=o_mqtt_user)
            e_mqtt_user.grid(column = 1, row = 1,sticky = tk.W)
            tk.Label(oframe, text = "MQTT password",font=('Arial', 12)).grid(column = 2, row = 1)
            e_mqtt_pass = tk.Entry(oframe,font=('Arial', 12),width=20, textvariable=o_mqtt_pass)
            e_mqtt_pass.grid(column = 3, row = 1,sticky = tk.W)
            e_mqtt_pass.configure(show="*")

            b_mqtt_retain = tk.Checkbutton(oframe,text="MQTT retain",font=('Arial', 12),variable=o_mqtt_retain)
            b_mqtt_retain.grid(column=0,row=2,sticky = tk.W)
            tk.Label(oframe, text = "MQTT discovery prefix",font=('Arial', 12)).grid(column = 1, row = 2,sticky = tk.E)
            e_discovery_prefix = tk.Entry(oframe,font=('Arial', 12),width=30, textvariable=o_discovery_prefix)
            e_discovery_prefix.grid(column = 2, row = 2,columnspan=3,sticky = tk.W)

            b_testrun = tk.Checkbutton(oframe,text="Test mode=do not send config",font=('Arial', 12),variable=o_testrun)
            b_testrun.grid(column=0,row=3,columnspan=2, sticky = tk.W)
            b_debug = tk.Checkbutton(oframe,text="Show debug messages",font=('Arial', 12),variable=o_debug)
            b_debug.grid(column=2,row=3,columnspan=2, sticky = tk.W)
            b_gen1 = tk.Checkbutton(oframe,text="Detect Gen1 devices",font=('Arial', 12),variable=o_gen1)
            b_gen1.grid(column=0,row=4,columnspan=2, sticky = tk.W)
            b_gen2 = tk.Checkbutton(oframe,text="Detect Gen2 devices",font=('Arial', 12),variable=o_gen2)
            b_gen2.grid(column=2,row=4,columnspan=2, sticky = tk.W)

            b_scan = tk.Button(aframe,text="Start detection loop",font=('Arial', 12), command=changeProvision)
            b_scan.grid(column=0,row=0,sticky=tk.W+tk.E)
            b_save = tk.Button(aframe,text="Save settings",font=('Arial', 12), command=saveSettings)
            b_save.grid(column=1,row=0,sticky=tk.W+tk.E)
            text_area = scrolledtext.ScrolledText(aframe,font=('Arial', 12), wrap=tk.WORD,width=(rwin-10))
            text_area.grid(column = 0, row = 1,columnspan=2,pady=2,padx=2,sticky = tk.W)
            text_area.insert(tk.INSERT,"Initializing, please wait...\n\n")
            text_area.configure(state ='disabled')
            aframe.columnconfigure(0, weight=1)
            aframe.rowconfigure(0, weight=1)
            aframe.rowconfigure(1, weight=1)

if app is not None:
   app.update()

if _mqttok==0: #paho-mqtt not installed, mqtt sending impossible
   printLn("Paho MQTT not found, fallback to test mode")
   settings.testrun = True

def syncguisettings():
    global app, pressedsave
    if (app is not None) and pressedsave:
       opts = ['mqtt_ip','mqtt_port','mqtt_user','mqtt_pass','discovery_prefix']
       for o in opts:
        try:
         ovar = str(app.getvar(name=o))
        except:
         ovar = None
        if ovar is not None:
            try:
             settings.data[o] = ovar
            except:
             pass

       opts = ['testrun','retain','gen1','gen2','debug'] #booleans
       for o in opts:
           try:
            ovar = (int(app.getvar(name=o))==1)
           except:
            ovar = None
           if ovar is not None:
            if o==opts[0]:
             settings.testrun = ovar
            elif o==opts[1]:
             settings.retain = ovar
            elif o==opts[2]:
             settings.gen1 = ovar
            elif o==opts[3]:
             settings.gen2 = ovar
            elif o==opts[4]:
             settings.debug = ovar

def connect_mqtt():
 global mqttclient1, app
 loopok2 = False
 syncguisettings()
 if settings.testrun==False:
  if settings.gen1:
   mqttclient1 = MQTTClient() #gen1
   mqttclient1.subscribechannel = settings.data['trigger_topic1']
   printLn("Connecting to MQTT server...")
   loopok2 = False
   try:
     if settings.data['mqtt_user'] != "" or settings.data['mqtt_pass'] != "":
      mqttclient1.username_pw_set(settings.data['mqtt_user'],settings.data['mqtt_pass'])
     mqttclient1.connect(settings.data['mqtt_ip'],int(settings.data['mqtt_port']),keepalive=60)
     mqttclient1.loop_start()
     loopok2 = True
   except Exception as e:
     printLn("Connection failed to MQTT server at "+str(settings.data['mqtt_ip'])+" "+str(e))
     return False
   if app is not None:
    app.update()
  if settings.gen2:
   mqttclient2 = MQTTClient() #gen2
   mqttclient2.subscribechannel = settings.data['trigger_topic2']
   if settings.gen1==False:
    mqttclient1 = mqttclient2
   printLn("Connecting to MQTT server...")
   loopok2 = False
   try:
     if settings.data['mqtt_user'] != "" or settings.data['mqtt_pass'] != "":
      mqttclient2.username_pw_set(settings.data['mqtt_user'],settings.data['mqtt_pass'])
     mqttclient2.connect(settings.data['mqtt_ip'],int(settings.data['mqtt_port']),keepalive=60)
     mqttclient2.loop_start()
     loopok2 = True
   except Exception as e:
     printLn("Connection failed! "+str(e))
     return False
   mqttclient3 = MQTTClientOnlineCheck() #gen2 online
   mqttclient3.subscribechannel = settings.data['trigger_topic3']
   printLn("Connecting to MQTT server...")
   loopok2 = False
   try:
     if settings.data['mqtt_user'] != "" or settings.data['mqtt_pass'] != "":
      mqttclient3.username_pw_set(settings.data['mqtt_user'],settings.data['mqtt_pass'])
     mqttclient3.connect(settings.data['mqtt_ip'],int(settings.data['mqtt_port']),keepalive=60)
     mqttclient3.loop_start()
     loopok2 = True
   except Exception as e:
     printLn("Connection failed! "+str(e))
 else:
  printLn("Test run without MQTT connection")
  loopok2 = True
  if settings.gen1:
   settings.shque.append("shellymotionsensor-60A42397667E")
   settings.shjsons["shellymotionsensor-60A42397667E"] = {"id":"shellymotionsensor-60A42397667E","model":"SHMOS-01","mac":"60A42397667E","ip":"192.168.2.32","new_fw":False,"fw_ver":"20211026-072015/v2.0.3@1dfb9313"}  
  if settings.gen2:
   settings.shque.append("shellyplus2pm-a8032abcf5f0")
   settings.shjsons["shellyplus2pm-a8032abcf5f0"] = {"id":1,"src":"shellyplus2pm-a8032abcf5f0","dst":"shellies_discovery","result":{"mqtt":{"enable":True,"topic_prefix":"shellyplus2pm-a8032abcf5f0","rpc_ntf":True,"status_ntf":True,"use_client_cert":False},"sys":{"device":{"name":None,"mac":"A8032ABCF5F0","fw_id":"20221206-141227/0.12.0-gafc2404","discoverable":True,"eco_mode":False,"addon_type":None}}}}
#   settings.shque.append("shellyplus1-a8032abcf5f0")
#   settings.shjsons["shellyplus1-a8032abcf5f0"] = {"id":1,"src":"shellyplus1-a8032abcf5f0","dst":"shellies_discovery","result":{"mqtt":{"enable":True,"topic_prefix":"shellyplus1-a8032abcf5f0","rpc_ntf":True,"status_ntf":True,"use_client_cert":False},"sys":{"device":{"name":None,"mac":"A8032ABCF5F0","fw_id":"20221206-141227/0.12.0-gafc2404","discoverable":True,"eco_mode":False,"addon_type":None}}}}

 if app is not None:
    app.update()
 return loopok2

loopok2 = connect_mqtt()
if loopok2==False:
   startprovision = False

if settings.gen1:
 filename = os.path.join( str(pathname) , settings.data['gen1_template_file'] )
 tf = TemplateDataFile( filename ) # init template database file for Gen1 devices
if settings.gen2:
 filename = os.path.join( str(pathname) , settings.data['gen2_template_file'] )
 tf2 = TemplateDataFile( filename ) # init template database file for Gen2 devices

if app is None: #console mode
   if loopok2:
    print("Starting eval loop, waiting Shelly devices to appear on MQTT announce... press CTRL-C to cancel")
    startprovision = True
   else:
    print("MQTT connection failed, alter settings and retry!")
    exit(0)
else:
   if loopok2:
    if startprovision==False:
     if guiautoprovision:
      changeProvision()
     else:
      printLn("\nPress start button to start detection loop...")
   else:
    printLn("\nMQTT connection failed, alter settings, close app if necessary and retry!")

decodinprog = False
while loopok:
  if app is not None:
   app.update()
  if startprovision:
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
         printLn(">>>GEN2 device "+str(di["shelly_id"])+" "+str(di["shelly_topic"])+" found")

         for i in range(len(mt)):
            mqttstr = {"topic": fill_template_str(mt[i]['topic'], di),"payload": fill_template_str(mt[i]['payload'], di)}
            settings.mqttsender.append(mqttstr)
        else:
         printLn("---ERROR: GEN2 device "+str(di["shelly_id"])+" "+str(di["shelly_topic"])+" template not found")

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
        if len(mt)<1: # fallback to generic description if mode specific not found
         mt = tf.get_templates(di["shelly_model"])
         if len(mt)>0:
          model = di["shelly_model"]

        if len(mt)>0:
         printLn(">>>GEN1 device "+str(di["shelly_ip"])+" "+str(model)+" "+str(di["shelly_id"])+" found")

         for i in range(len(mt)):
            mqttstr = {"topic": fill_template_str(mt[i]['topic'], di),"payload": fill_template_str(mt[i]['payload'], di)}
            settings.mqttsender.append(mqttstr)
        else:
         printLn("---ERROR: GEN1 device "+str(di["shelly_ip"])+" "+str(model)+" "+str(di["shelly_id"])+" template not found")

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
      printLn(str(settings.mqttsender[0]['topic'])+":"+str(settings.mqttsender[0]['payload'])) # debug, only print MQTT
     else:
      t = str(settings.mqttsender[0]['topic'])
      if settings.data['discovery_prefix'] in t:
       ret = settings.retain
      else:
       ret = False # retain not needed if it is not discovery configuration
      if ret:
       qosl = 1
      else:
       qosl = 0
      (mres,mid) = mqttclient1.publish(settings.mqttsender[0]['topic'],settings.mqttsender[0]['payload'],retain=ret,qos=qosl)
    except:
     mres = 1
    if mres==0:
     try:
      del settings.mqttsender[0]
     except:
      pass
  time.sleep(0.01)
