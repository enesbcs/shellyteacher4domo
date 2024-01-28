# ShellyTeacher 4 Domoticz common function library
import re
import json
try:
 import urllib
except:
 pass

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
      print("JSON decode error: "+str(e)+" "+str(msg2))
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
            print(str(e))
        if tfe is False or len(self.template)<1:
           self.templatename = ""
        return self.template

class Tasmota_Discovery:
    template = {}
    mac = ""
    config = {}
    sensors = {}

    STAT_EMPTY = 0
    STAT_CONF  = 1
    STAT_SENS  = 2
    STAT_CONF_SENS = 3
    STAT_REPOK = 4

    def __init__(self, mac):
        self.mac = mac
        self.state = self.STAT_EMPTY
        self.template = []

    def getmac(self):
        return self.mac

    def getstate(self):
        return self.state

    def add_data(self,conftop,conf):
           try:
             if 'config' in conftop:
              if type(conf)==dict:
               self.config = conf
               self.state  = self.state | self.STAT_CONF
              elif type(conf)==str and "{" in conf:
               self.config = json.loads(conf)
               self.state  = self.state | self.STAT_CONF
             elif 'sensors' in conftop:
              if type(conf)==dict:
               self.sensors = conf
               self.state  = self.state | self.STAT_SENS
              elif type(conf)==str and "{" in conf:
               self.sensors = json.loads(conf)
               self.state  = self.state | self.STAT_SENS
           except Exception as e:
            print(e)

    def get_templates(self):
       if self.state > self.STAT_CONF:
        self.template = []
        try:
            tdict = {}
            tdict['prefix'] = self.config['tp'][0]
            tdict['topic'] = self.config['t']
            tasmodict = {}
            tasmodict['cmd_topic'] = fill_template_str(self.config['ft'],tdict)
            tdict['prefix'] = self.config['tp'][1]
            tasmodict['stat_topic'] = fill_template_str(self.config['ft'],tdict)
            tdict['prefix'] = self.config['tp'][2]
            tasmodict['tele_topic'] = fill_template_str(self.config['ft'],tdict)
            if tasmodict['cmd_topic'][-1] != "/":
               tasmodict['cmd_topic'] += "/"
            if tasmodict['stat_topic'][-1] != "/":
               tasmodict['stat_topic'] += "/"
            if tasmodict['tele_topic'][-1] != "/":
               tasmodict['tele_topic'] += "/"
            tasmodict['mac'] = self.config['mac']
            tasmodict['model'] = self.config['md']
            tasmodict['name'] = self.config['dn']
            try:
             tasmodict['onln'] = self.config['onln']
            except:
             tasmodict['onln'] = "Online"
            try:
             tasmodict['ofln'] = self.config['ofln']
            except:
             tasmodict['ofln'] = "Offline"
            tasmodict['subname'] = ""
#            print(tasmodict)#debug
            try:
                     tmt = {}
                     tmt["name"] = tasmodict['name'] + " Online"
                     tmt["stat_t"] = tasmodict['tele_topic'] + "LWT"
                     tmt["pl_on"] = tasmodict["onln"]
                     tmt["pl_off"] = tasmodict["ofln"]
                     tmt["uniq_id"] = tasmodict["mac"]+"_online"
                     tmt['device'] = {}
                     tmt['device']['name'] = tasmodict['name']
                     tmt['device']['identifiers'] = []
                     tmt['device']['identifiers'].append(tasmodict['mac'])
                     tmt['device']['model'] = tasmodict['model']
                     tmt['device']['sw_version'] = self.config['sw']
                     mt = {}
                     mt['topic']   = "%discovery_prefix%/binary_sensor/" + tmt["uniq_id"] + "/config"
                     mt['payload'] = json.dumps(tmt)
                     self.template.append(mt)
            except:
             pass
            if 'btn' in self.config: #buttons
              for i in range(0,len(self.config['btn'])):
                  if int(self.config['btn'][i])>0:
                     try:
                      subname = str(self.config['fn'][i])
                      if subname is None or str(subname) == "null":
                         subname = ""
                     except:
                      subname = ""
                     if subname == "":
                        subname = tasmodict['name']
                     tasmodict['subname'] = subname + " Button"+str(i+1)
                     tmt = {}
                     tmt["name"] = tasmodict['subname']
                     tmt["stat_t"] = tasmodict['stat_topic'] + "BUTTON"+str(i+1)
                     tmt["avty_t"] = tasmodict['tele_topic'] + "LWT"
                     tmt["pl_avail"] = tasmodict["onln"]
                     tmt["pl_not_avail"] = tasmodict["ofln"]
                     tmt["pl_on"] = "TOGGLE"
                     tmt["off_delay"] = 1
                     tmt["uniq_id"] = tasmodict["mac"]+"_BTN_"+str(i+1)
                     mt = {}
                     mt['topic']   = "%discovery_prefix%/binary_sensor/" + tmt["uniq_id"] + "/config"
                     mt['payload'] = json.dumps(tmt)
                     tasmodict['subname'] = "" #reset value at the end
                     self.template.append(mt)
            if 'swc' in self.config: #switches
              for i in range(0,len(self.config['swc'])):
                  if int(self.config['swc'][i])>0:
                     try:
                      subname = str(self.config['swn'][i])
                      if subname is None or str(subname) == "null":
                         subname = ""
                     except:
                      subname = ""
                     if subname == "":
                        subname = tasmodict['name'] + " Switch"+str(i+1)
                     tasmodict['subname'] = subname
                     tmt = {}
                     tmt["name"] = tasmodict['subname']
                     tmt["stat_t"] = tasmodict['stat_topic'] + "SWITCH"+str(i+1)
                     tmt["avty_t"] = tasmodict['tele_topic'] + "LWT"
                     tmt["pl_avail"] = tasmodict["onln"]
                     tmt["pl_not_avail"] = tasmodict["ofln"]
                     tmt["pl_on"] = "ON"
                     tmt["pl_off"] = "OFF"
                     tmt["uniq_id"] = tasmodict["mac"]+"_SW_"+str(i+1)
                     mt = {}
                     mt['topic']   = "%discovery_prefix%/binary_sensor/" + tmt["uniq_id"] + "/config"
                     mt['payload'] = json.dumps(tmt)
                     tasmodict['subname'] = "" #reset value at the end
                     self.template.append(mt)
            if 'rl' in self.config: #relays
              standard = True
              if sum(self.config['rl'])==1:
               standard = False #Power1 is not working if config has only one relay
              for i in range(0,len(self.config['rl'])):
                  if int(self.config['rl'][i])>0:
                     try:
                      subname = str(self.config['fn'][i])
                      if subname is None or str(subname) == "null":
                         subname = ""
                     except:
                      subname = ""
                     if subname == "":
                        subname = tasmodict['name'] + " Relay"+str(i+1)
                     tasmodict['subname'] = subname
                     tmt = {}
                     tmt["name"] = tasmodict['subname']
                     if standard == False and i==0:
                      tmt["stat_t"] = tasmodict['stat_topic'] + "POWER"
                      tmt["cmd_t"] = tasmodict['cmd_topic'] + "POWER"
                     else:
                      tmt["stat_t"] = tasmodict['stat_topic'] + "POWER"+str(i+1)
                      tmt["cmd_t"] = tasmodict['cmd_topic'] + "POWER"+str(i+1)
                     tmt["avty_t"] = tasmodict['tele_topic'] + "LWT"
                     tmt["pl_avail"] = tasmodict["onln"]
                     tmt["pl_not_avail"] = tasmodict["ofln"]
                     tmt["pl_on"] = "ON"
                     tmt["pl_off"] = "OFF"
                     tmt["uniq_id"] = tasmodict["mac"]+"_RL_"+str(i+1)
                     mt = {}
                     mt['topic']   = "%discovery_prefix%/switch/" + tmt["uniq_id"] + "/config"
                     mt['payload'] = json.dumps(tmt)
                     tasmodict['subname'] = "" #reset value at the end
                     self.template.append(mt)
            if 'sn' in self.sensors: #sensor data exists
               for key in self.sensors['sn']:
                  if type(self.sensors['sn'][key]) == dict:
#                   print(key, self.sensors['sn'][key], type(self.sensors['sn'][key]))
                   for subkey in self.sensors['sn'][key]:
                       sval = self.sensors['sn'][key][subkey]
                       if type(sval) != dict and subkey.lower() != "dewpoint":
#                          print(subkey,sval)
                          tmt = {}
                          tmt['name'] = tasmodict['name'] + " " + key + " " + subkey
                          tmt['stat_t'] = tasmodict['tele_topic'] + "SENSOR"
                          tmt['value_template'] = "{{ value_json." + key + "." +subkey +" }}"
                          tmt['stat_cla'] = 'measurement'
                          subkeyl = subkey.lower()
                          if "power" in subkeyl:
                             tmt["unit_of_meas"] = "W"
                             tmt["dev_cla"] = "power"
                          elif subkeyl == "temperature":
                             try:
                              tmt["unit_of_meas"] = self.sensors['sn']['TempUnit']
                             except:
                              tmt["unit_of_meas"] = "C"
                             tmt["dev_cla"] = "temperature"
                          elif subkeyl == "humidity":
                             tmt["unit_of_meas"] = "%"
                             tmt["dev_cla"] = "humidity"
                          elif subkeyl == "pressure":
                             try:
                              tmt["unit_of_meas"] = self.sensors['sn']['PressureUnit']
                             except:
                              tmt["unit_of_meas"] = "hPa"
                             tmt["dev_cla"] = "atmospheric_pressure"
                          elif subkeyl in ["total","yesterday","today"]:
                             tmt["unit_of_meas"] = "kWh"
                             tmt["dev_cla"] = "energy"
                          elif subkeyl == "period":
                             tmt["unit_of_meas"] = "Wh"
                             tmt["dev_cla"] = "energy"
                          elif subkeyl == "voltage":
                             tmt["unit_of_meas"] = "V"
                             tmt["dev_cla"] = "voltage"
                          elif subkeyl == "current":
                             tmt["unit_of_meas"] = "A"
                             tmt["dev_cla"] = "current"
                          elif subkeyl == "illuminance":
                             tmt["unit_of_meas"] = "lux"
                             tmt["dev_cla"] = "illuminance"
                          if (subkeyl in ['temperature','humidity','pressure','energy']) or ("power" in subkeyl):
                             tmt['device'] = {}
                             tmt['device']['name'] = tasmodict['name'] + " " + key
                             tmt['device']['identifiers'] = []
                             tmt['device']['identifiers'].append(tasmodict['mac'] + "-" + key)
                          tmt["uniq_id"] = tasmodict['mac'] + "-" + key.lower() + "-" + subkeyl
                          mt = {}
                          mt['topic']   = "%discovery_prefix%/sensor/" + tasmodict['mac'] + "-" + key.lower() + "/" + subkeyl + "/config"
                          mt['payload'] = json.dumps(tmt)
                          self.template.append(mt)

            self.state = self.state | self.STAT_REPOK
        except Exception as e:
         print("get_template",str(e))
        return self.template

#td = Tasmota_Discovery('3C71BFF01A7C')
#td.add_data('tasmota/discovery/3C71BFF01A7C/config','{"ip":"192.168.2.8","dn":"thermostat","fn":["heating","motion","display",null,null,null,null,null],"hn":"thermostat-6780","mac":"3C71BFF01A7C","md":"ESP32-DevKit","ty":0,"if":0,"ofln":"Offline","onln":"Online","state":["OFF","ON","TOGGLE","HOLD"],"sw":"13.2.0.1","t":"thermostat","ft":"%prefix%/%topic%/","tp":["cmnd","stat","tele"],"rl":[1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],"swc":[-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1],"swn":[null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null],"btn":[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],"so":{"4":0,"11":0,"13":0,"17":0,"20":0,"30":0,"68":0,"73":0,"82":0,"114":0,"117":0},"lk":0,"lt_st":0,"sho":[],"sht":[[0,0,0],[0,0,0],[0,0,0],[0,0,0]],"ver":1}')
#td.add_data('tasmota/discovery/3C71BFF01A7C/sensors','{"sn":{"Time":"2023-12-31T08:57:03","Switch1":"ON","Switch2":"OFF","HTU21":{"Temperature":20.7,"Humidity":40.9,"DewPoint":7.0},"TempUnit":"C"},"ver":1}')
#print(td.get_templates())
