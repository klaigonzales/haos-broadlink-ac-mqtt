#!/usr/bin/python
import os
import time
import sys
import logging
import argparse
import yaml
import paho.mqtt.client as mqtt
import tempfile
import json
import traceback
import socket

sys.path.insert(1, os.path.join(os.path.dirname(os.path.realpath(__file__)),'classes','broadlink'))
import broadlink_ac_mqtt.classes.broadlink.ac_db as broadlink




logger = logging.getLogger(__name__)

config  = {}	
device_objects = {}





def parse_device(device):
	"""Return (key, host, mac, name) for a configured device, or raise.

	The key is the parsed MAC as bare lower-case hex, which is byte-for-byte
	what ac_db reports as status['macaddress'] and therefore what the Home
	Assistant command topics are built from -- whatever case or spacing the
	config used.

	Raises KeyError/TypeError/ValueError for anything permanently wrong, so
	callers can tell a bad config entry, which must never be retried, from an
	unreachable device, which must be.
	"""
	ip = device['ip']
	if not isinstance(ip, str) or not ip.strip():
		raise ValueError("ip must be a non-empty string, got %r" % (ip,))

	port = device['port']
	##bool is a subclass of int, so "port: true" would otherwise become port 1.
	##Floats are refused outright rather than truncated, which also keeps
	##"port: .inf" from reaching int() and raising OverflowError -- that is
	##outside the exception contract above and would escape our callers.
	if isinstance(port, bool) or not isinstance(port, (int, str)):
		raise ValueError("port must be a whole number, got %r" % (port,))

	##int() so a quoted "80" from YAML still works.
	port = int(port)
	##A port outside this range can never connect, so it belongs on the
	##malformed path rather than being retried forever as merely unreachable.
	if not 0 < port < 65536:
		raise ValueError("port out of range: %r" % (port,))
	host = (ip, port)

	mac = bytearray.fromhex(device['mac'])
	##fromhex is happy with any even-length string, so a truncated MAC like
	##"aabb" parses. ac_db.send_packet then indexes all six bytes and raises
	##IndexError, which reads like a transient failure and gets retried forever.
	if len(mac) != 6:
		raise ValueError("mac must be 6 bytes, got %s in %r" % (len(mac), device['mac']))

	return mac.hex(), host, mac, device['name']


class AcToMqtt:
	previous_status = {}
	last_update = {}
	failed_polls = {}
	availability_status = {}
	device_startup_attempts = 5

	def __init__(self,config):
		self.config = config
		##connect_mqtt() starts the paho network thread before start() assigns the
		##real device map, so callbacks must always find an attribute here.
		self.device_objects = {}
		""
	def test(self,config):
		
		
		for device in config['devices']:
			
			device_bla = broadlink.gendevice(devtype=0xFFFFFFF, host=(device['ip'],device['port']),mac = bytearray.fromhex(device['mac']), name=device['name'])		
			status = device_bla.set_temperature(32)
			#print status

	
	def discover(self):		

		##Go discovery
		discovered_devices = broadlink.discover(timeout=5,bind_to_ip=self.config['bind_to_ip'])			
		devices = {}
		
		if discovered_devices == None:
			error_msg = "No Devices Found, make sure you on the same network segment"
			logger.debug(error_msg)
			
			#print "nothing found"
			sys.exit()
			
		##Make sure correct device id 
		for device in discovered_devices:		  			
			if device.devtype in broadlink.SUPPORTED_AC_DEVTYPES or (isinstance(device.devtype, int) and (device.devtype & 0xFF00) == 0x4E00):
				devices[device.status['macaddress']] = device				
		
		return devices
		

	
	def make_device_objects(self,device_list = None,attempts = None):
		device_objects = {}

		if  device_list == [] or device_list == None:
			error_msg = " Cannot make device objects, empty list given"
			logger.error(error_msg)
			sys.exit()

		##"or" would turn an explicit attempts=0 back into the default.
		if attempts is None:
			attempts = self.device_startup_attempts

		for device in device_list:
			##A malformed entry is permanent: report it once instead of burning
			##<attempts> connection attempts on it every time we are called.
			try:
				key, host, mac, name = parse_device(device)
			except (KeyError, TypeError, ValueError) as e:
				logger.error("Skipping malformed device entry %r: %s" % (device, e))
				continue

			for attempt in range(1, attempts + 1):
				try:
					device_objects[key] = broadlink.gendevice(devtype=0x4E2a, host=host, mac=mac, name=name, update_interval=self.config['update_interval'])
					break
				##Deliberately broad: an unreachable unit must never abort startup of
				##the others, and ac_db signals failure in more ways than ConnectError
				##(a failed auth() makes __init__ "return False", which is a TypeError).
				except Exception as e:
					logger.warning("Starting device %s at %s:%s failed on attempt %s/%s: %s" % (device['mac'], device['ip'], device['port'], attempt, attempts, e))
					logger.debug(traceback.format_exc())
			else:
				logger.error("Skipping device %s at %s:%s after %s failed startup attempts" % (device['mac'], device['ip'], device['port'], attempts))

		return device_objects

	def stop(self):

		##Say goodbye ourselves - a clean disconnect never fires the will, so
		##without this HA waits out the keepalive before marking us offline.
		##(found in huncrys' fork). Its own try, so a goodbye that fails still
		##leaves the disconnect below to run, and publish() only queues the
		##message: disconnecting straight after it can drop it on the floor.
		try:
			if hasattr(self, 'device_objects') and self.device_objects:
				for key in self.device_objects:
					try:
						self._mqtt.publish(self.config["mqtt_topic_prefix"] + key + '/availability', 'offline', qos=0, retain=True)
					except Exception:
						pass
			info = self._mqtt.publish(self.config["mqtt_topic_prefix"]+'LWT','offline',qos=0,retain=True)
			info.wait_for_publish(timeout=5)
			##wait_for_publish() returns quietly when it times out, so ask outright.
			##Nothing to retry against a broker that will not take it while we are
			##on our way out, but HA left showing a stale "online" should at least
			##say why in the log rather than be a silent shrug.
			if not info.is_published():
				logger.warning("Gave up waiting to publish offline status; HA may show us online until the keepalive expires")
		except Exception as e:
			logger.warning("Could not publish offline status: %s" % e)

		try:
			self._mqtt.disconnect()
			##connect_mqtt() called loop_start(); nothing ever stopped that thread.
			##It is a daemon so the process still exits, but only the interpreter
			##tearing down was ending it. Shut it down where we started it.
			self._mqtt.loop_stop()
		except:
			""
				
	def start (self,config, devices = None):
		
		##Not "devices or {}": when the caller handed us its own empty dict we must
		##keep that very object, because recover_missing_devices() fills it in place
		##and the paho thread reads it through this attribute.
		self.device_objects = devices if devices is not None else {}
		self.config = config
		
		##If there no devices so throw error
		if not devices:
			logger.error("No devices to poll, either enable discovery or add them to config")
			##Caller loops on us without a delay of its own, so pace ourselves here
			##instead of spinning a core while every device is unreachable. "or 1"
			##because update_interval 0 means "poll flat out", which is meaningless
			##with nothing to poll and would peg a core on a Pi.
			time.sleep(self.config["update_interval"] or 1)
			return 0
		else:
			logger.debug ("Following devices configured %s" % repr(devices))
		
		##we are alive ##Update PID file			
		try:
			
			for key in devices:
				

				device = devices[key]
				##Just check status on every update interval
				if key in self.last_update:
					logger.debug("Checking %s for timeout" % key)
					if (self.last_update[key] + self.config["update_interval"]) > time.time():
						logger.debug("Timeout %s not done, so lets wait a abit : %s : %s" %(self.config["update_interval"],self.last_update[key] + self.config["update_interval"],time.time()))				
						time.sleep(0.5)
						continue
					else:
						""
						#print "timeout done"					
			
				##Get the status, the global update interval is used as well to reduce requests to aircons as they slow
				##Isolate each device: a timeout/error talking to one unit must
				##not abort polling of the others (previously a single
				##ConnectTimeout broke the whole loop and every device went
				##"unavailable" in Home Assistant until a restart).
				try:
					status = device.get_ac_status()
				except Exception as e:
					self.failed_polls[key] = self.failed_polls.get(key, 0) + 1
					logger.warning("Polling device %s failed (%s consecutive failures): %s" % (key, self.failed_polls[key], e))
					logger.debug(traceback.format_exc())
					if self.failed_polls[key] >= 3:
						if self.availability_status.get(key) != 'offline':
							self.availability_status[key] = 'offline'
							self._publish(self.config["mqtt_topic_prefix"] + key + '/availability', 'offline', retain=True)
					continue

				#print status
				if status:
					self.failed_polls[key] = 0
					if self.availability_status.get(key) != 'online':
						self.availability_status[key] = 'online'
						self._publish(self.config["mqtt_topic_prefix"] + key + '/availability', 'online', retain=True)
					##Update last time checked
					self.last_update[key] = time.time()
					self.publish_mqtt_info(status)

				else:
					logger.debug("No status")				
				
		except Exception as e:					
			logger.critical(e)	
			logger.debug(traceback.format_exc())
			##Something went wrong..... 
			

		return 1
			
				
	def dump_homeassistant_config_from_devices(self,devices):	
		
		if devices == {}:
			print ("No devices defined")
			sys.exit()
		
		devices_array = self.make_devices_array_from_devices(devices)
		if devices_array ==  {}:
			print ("something went wrong, no devices found")
			sys.exit()
			
		print ("**************** Start copy below ****************")
		a = []
		for key in devices_array:
			##Echo					
			device = devices_array[key]
			device['platform'] = 'mqtt'			
			a.append(device)
		print (yaml.dump({'climate':a}))
		print ("**************** Stop copy above ****************")
		
	def make_devices_array_from_devices(self,devices):
		
		devices_array = {}
		
		for device in devices.values():
			##topic = self.config["mqtt_auto_discovery_topic"]+"/climate/"+device.status["macaddress"]+"/config"
			##An AC with no name used to abort auto discovery for every device: the
			##unnamed branch left name a str and the next line called .decode() on
			##it. Both ways of being unnamed land here -- config leaves it None, and
			##discover() assigns the raw MAC *bytearray* ("if not name: name = mac"),
			##which has no .encode(). Anything that is not a usable str means
			##unnamed, and status["macaddress"] is the readable hex of that same MAC.
			##Strip before the fallback, not after: a name that is entirely
			##non-ascii ("Кондиционер") reduces to nothing and would otherwise
			##announce a nameless entity to HA.
			name = device.name if isinstance(device.name,str) else ""
			name = name.encode('ascii','ignore').decode('utf-8').strip()
			name = name or device.status["macaddress"]

			device_array = {
				"name": name,
				"unique_id": f"broadlink_ac_{device.status['macaddress']}",
				"mode_command_topic": self.config["mqtt_topic_prefix"] + device.status["macaddress"] + "/mode_homeassistant/set",
				"temperature_command_topic": self.config["mqtt_topic_prefix"] + device.status["macaddress"] + "/temp/set",
				"fan_mode_command_topic": self.config["mqtt_topic_prefix"] + device.status["macaddress"] + "/fanspeed_homeassistant/set",
				"swing_mode_command_topic": self.config["mqtt_topic_prefix"] + device.status["macaddress"] + "/fixation_v/set",
				"current_temperature_topic": self.config["mqtt_topic_prefix"] + device.status["macaddress"] + "/ambient_temp/value",
				"mode_state_topic": self.config["mqtt_topic_prefix"] + device.status["macaddress"] + "/mode_homeassistant/value",
				"temperature_state_topic": self.config["mqtt_topic_prefix"] + device.status["macaddress"] + "/temp/value",
				"fan_mode_state_topic": self.config["mqtt_topic_prefix"] + device.status["macaddress"] + "/fanspeed_homeassistant/value",
				"swing_mode_state_topic": self.config["mqtt_topic_prefix"] + device.status["macaddress"] + "/fixation_v/value",
				"fan_modes": ["Auto", "Low", "Medium", "High", "Turbo", "Mute"],
				"modes": ["off", "cool", "heat", "fan_only", "dry", "auto"],
				"swing_modes": ["TOP", "MIDDLE1", "MIDDLE2", "MIDDLE3", "BOTTOM", "SWING", "AUTO"],
				"max_temp": 32.0,
				"min_temp": 16.0,
				"temperature_unit": "C",
				"precision": 0.1,
				"temp_step": 0.5,
				"device": {
					"identifiers": [f"broadlink_ac_{device.status['macaddress']}"],
					"name": name,
					"model": "Broadlink AC Controller",
					"manufacturer": "Broadlink",
					"sw_version": broadlink.version,
				},
				"pl_avail": "online",
				"pl_not_avail": "offline",
				"availability_topic": self.config["mqtt_topic_prefix"] + "LWT",
			}
			
			devices_array[device.status["macaddress"]] = device_array
			
		return devices_array

	def publish_mqtt_auto_discovery(self, devices):
		if not devices:
			logger.error("No devices to announce, either enable discovery or add them to config")
			return

		retain = bool(self.config.get("mqtt_auto_discovery_topic_retain", False))
		discovery_prefix = self.config.get("mqtt_auto_discovery_topic", "homeassistant")
		topic_prefix = self.config.get("mqtt_topic_prefix", "/aircon")
		if not topic_prefix.endswith('/'):
			topic_prefix += '/'

		logger.debug("HA config Retain set to: " + str(retain))

		for device in devices.values():
			mac = device.status["macaddress"]
			name = device.name if isinstance(device.name, str) else ""
			name = name.encode('ascii', 'ignore').decode('utf-8').strip()
			name = name or mac

			device_info = {
				"identifiers": [f"broadlink_ac_{mac}"],
				"name": name,
				"model": "Broadlink AC Controller",
				"manufacturer": "Broadlink",
				"sw_version": broadlink.version,
			}
			availability_topic = f"{topic_prefix}{mac}/availability"

			# 1. Climate Entity
			climate_config = {
				"name": name,
				"unique_id": f"broadlink_ac_{mac}",
				"mode_command_topic": f"{topic_prefix}{mac}/mode_homeassistant/set",
				"temperature_command_topic": f"{topic_prefix}{mac}/temp/set",
				"fan_mode_command_topic": f"{topic_prefix}{mac}/fanspeed_homeassistant/set",
				"swing_mode_command_topic": f"{topic_prefix}{mac}/fixation_v/set",
				"current_temperature_topic": f"{topic_prefix}{mac}/ambient_temp/value",
				"mode_state_topic": f"{topic_prefix}{mac}/mode_homeassistant/value",
				"temperature_state_topic": f"{topic_prefix}{mac}/temp/value",
				"fan_mode_state_topic": f"{topic_prefix}{mac}/fanspeed_homeassistant/value",
				"swing_mode_state_topic": f"{topic_prefix}{mac}/fixation_v/value",
				"fan_modes": ["Auto", "Low", "Medium", "High", "Turbo", "Mute"],
				"modes": ["off", "cool", "heat", "fan_only", "dry", "auto"],
				"swing_modes": ["TOP", "MIDDLE1", "MIDDLE2", "MIDDLE3", "BOTTOM", "SWING", "AUTO"],
				"max_temp": 32.0,
				"min_temp": 16.0,
				"temperature_unit": "C",
				"precision": 0.1,
				"temp_step": 0.5,
				"device": device_info,
				"pl_avail": "online",
				"pl_not_avail": "offline",
				"availability_topic": availability_topic,
			}
			self._publish(f"{discovery_prefix}/climate/{mac}/config", json.dumps(climate_config), retain=retain)

			# 2. Ambient Temperature Sensor
			temp_sensor_config = {
				"name": f"{name} Temperature",
				"unique_id": f"broadlink_ac_{mac}_ambient_temp",
				"device_class": "temperature",
				"state_class": "measurement",
				"unit_of_measurement": "°C",
				"state_topic": f"{topic_prefix}{mac}/ambient_temp/value",
				"availability_topic": availability_topic,
				"pl_avail": "online",
				"pl_not_avail": "offline",
				"device": device_info,
			}
			self._publish(f"{discovery_prefix}/sensor/{mac}_temp/config", json.dumps(temp_sensor_config), retain=retain)

			# 3. Display (Light) Switch
			display_switch_config = {
				"name": f"{name} Display",
				"unique_id": f"broadlink_ac_{mac}_display",
				"icon": "mdi:television-ambient-light",
				"command_topic": f"{topic_prefix}{mac}/display/set",
				"state_topic": f"{topic_prefix}{mac}/display/value",
				"payload_on": "ON",
				"payload_off": "OFF",
				"state_on": "ON",
				"state_off": "OFF",
				"availability_topic": availability_topic,
				"pl_avail": "online",
				"pl_not_avail": "offline",
				"device": device_info,
			}
			self._publish(f"{discovery_prefix}/switch/{mac}_display/config", json.dumps(display_switch_config), retain=retain)

			# 4. Health / Ionizer Switch
			health_switch_config = {
				"name": f"{name} Health",
				"unique_id": f"broadlink_ac_{mac}_health",
				"icon": "mdi:air-filter",
				"command_topic": f"{topic_prefix}{mac}/health/set",
				"state_topic": f"{topic_prefix}{mac}/health/value",
				"payload_on": "ON",
				"payload_off": "OFF",
				"state_on": "ON",
				"state_off": "OFF",
				"availability_topic": availability_topic,
				"pl_avail": "online",
				"pl_not_avail": "offline",
				"device": device_info,
			}
			self._publish(f"{discovery_prefix}/switch/{mac}_health/config", json.dumps(health_switch_config), retain=retain)

			# 5. Turbo Switch
			turbo_switch_config = {
				"name": f"{name} Turbo",
				"unique_id": f"broadlink_ac_{mac}_turbo",
				"icon": "mdi:fan-speed-3",
				"command_topic": f"{topic_prefix}{mac}/turbo/set",
				"state_topic": f"{topic_prefix}{mac}/turbo/value",
				"payload_on": "ON",
				"payload_off": "OFF",
				"state_on": "ON",
				"state_off": "OFF",
				"availability_topic": availability_topic,
				"pl_avail": "online",
				"pl_not_avail": "offline",
				"device": device_info,
			}
			self._publish(f"{discovery_prefix}/switch/{mac}_turbo/config", json.dumps(turbo_switch_config), retain=retain)

			# 6. Mute Switch
			mute_switch_config = {
				"name": f"{name} Mute",
				"unique_id": f"broadlink_ac_{mac}_mute",
				"icon": "mdi:volume-mute",
				"command_topic": f"{topic_prefix}{mac}/mute/set",
				"state_topic": f"{topic_prefix}{mac}/mute/value",
				"payload_on": "ON",
				"payload_off": "OFF",
				"state_on": "ON",
				"state_off": "OFF",
				"availability_topic": availability_topic,
				"pl_avail": "online",
				"pl_not_avail": "offline",
				"device": device_info,
			}
			self._publish(f"{discovery_prefix}/switch/{mac}_mute/config", json.dumps(mute_switch_config), retain=retain)

			# 7. Sleep Switch
			sleep_switch_config = {
				"name": f"{name} Sleep",
				"unique_id": f"broadlink_ac_{mac}_sleep",
				"icon": "mdi:sleep",
				"command_topic": f"{topic_prefix}{mac}/sleep/set",
				"state_topic": f"{topic_prefix}{mac}/sleep/value",
				"payload_on": "ON",
				"payload_off": "OFF",
				"state_on": "ON",
				"state_off": "OFF",
				"availability_topic": availability_topic,
				"pl_avail": "online",
				"pl_not_avail": "offline",
				"device": device_info,
			}
			self._publish(f"{discovery_prefix}/switch/{mac}_sleep/config", json.dumps(sleep_switch_config), retain=retain)

			# 8. Clean Switch
			clean_switch_config = {
				"name": f"{name} Clean",
				"unique_id": f"broadlink_ac_{mac}_clean",
				"icon": "mdi:broom",
				"command_topic": f"{topic_prefix}{mac}/clean/set",
				"state_topic": f"{topic_prefix}{mac}/clean/value",
				"payload_on": "ON",
				"payload_off": "OFF",
				"state_on": "ON",
				"state_off": "OFF",
				"availability_topic": availability_topic,
				"pl_avail": "online",
				"pl_not_avail": "offline",
				"device": device_info,
			}
			self._publish(f"{discovery_prefix}/switch/{mac}_clean/config", json.dumps(clean_switch_config), retain=retain)

	def publish_mqtt_info(self,status,force_update = False) :	
		##If auto discovery is used, then always update
		if not force_update:
			force_update = True if "mqtt_auto_discovery_topic" in self.config and self.config["mqtt_auto_discovery_topic"] else False

		logger.debug("Force update is: " + str(force_update))

		##Publish all values in status
		for key in status:
			##Make sure its a string
			value = status[key]				
		 
			##check if device already in previous_status
			if not force_update and status['macaddress'] in self.previous_status:
				##Check if key in state
				if key in self.previous_status[status['macaddress']]:					
					##If the values are same, skip it to make mqtt less chatty #17
				
					if self.previous_status[status['macaddress']][key] == value:
						#print ("value same key:%s, value:%s vs : %s" %  (key,value,self.previous_status[status['macaddress']][key]))					
						continue
					else:
						""
						#print ("value NOT Same key:%s, value:%s vs : %s" %  (key,value,self.previous_status[status['macaddress']][key]))										
			
			pubResult = self._publish(self.config["mqtt_topic_prefix"] + status['macaddress']+'/'+key+ '/value',value)			
			
			
			if pubResult != None:					
				logger.warning('Publishing Result: "%s"' % mqtt.error_string(pubResult))
				if pubResult == mqtt.MQTT_ERR_NO_CONN:
					self.connect_mqtt()
					
				break
			
		##Set previous to current
		self.previous_status[status['macaddress']] = status
		##Per-device availability
		self._publish(self.config["mqtt_topic_prefix"] + status['macaddress'] + '/availability', 'online', retain=True)
		
		return 

		#self._publish(binascii.hexlify(status['macaddress'])+'/'+ 'temp/value',status['temp']);
				
				
	def _publish(self,topic,value,retain=False,qos=0):
		payload = value
		logger.debug('publishing on topic "%s", data "%s"' % (topic, payload))			
		pubResult = self._mqtt.publish(topic, payload=payload, qos=qos, retain=retain)
		
		##If there error, then debug log and return not None
		if pubResult[0] != 0:				
			logger.debug('Publishing Result: "%s"' % mqtt.error_string(pubResult[0]))
			return pubResult[0]
			
	def connect_mqtt(self):
	
		##Setup client
		##paho-mqtt 2.0 made callback_api_version mandatory and changed the
		##Client() signature. We opt into the legacy VERSION1 callback API so
		##the existing on_connect/on_message/on_publish signatures keep working,
		##while staying compatible with paho-mqtt 1.x (which has no such kwarg).
		try:
			self._mqtt = mqtt.Client(
				callback_api_version=mqtt.CallbackAPIVersion.VERSION1,
				client_id=self.config["mqtt_client_id"],
				clean_session=True,
				userdata=None,
			)
		except (AttributeError, TypeError):
			##paho-mqtt < 2.0: no CallbackAPIVersion enum / kwarg
			self._mqtt = mqtt.Client(
				client_id=self.config["mqtt_client_id"],
				clean_session=True,
				userdata=None,
			)
		
		
		##Set last will and testament
		self._mqtt.will_set(self.config["mqtt_topic_prefix"]+"LWT","offline",True)
		
		##Auth		
		if self.config["mqtt_user"] and self.config["mqtt_password"]:			
			self._mqtt.username_pw_set(self.config["mqtt_user"],self.config["mqtt_password"])
				
		
		##Setup callbacks
		self._mqtt.on_connect = self._on_mqtt_connect
		self._mqtt.on_message = self._on_mqtt_message
		self._mqtt.on_log = self._on_mqtt_log
		##on_subscribed is not a paho callback - the real name is on_subscribe, so the
		##hook has never fired. (found in ybeapps' fork)
		self._mqtt.on_subscribe = self._mqtt_on_subscribe
		
		##Connect
		logger.debug("Coneccting to MQTT: %s with client ID = %s" % (self.config["mqtt_host"],self.config["mqtt_client_id"]))
		##Exponential backoff for automatic reconnects handled by paho's loop.
		self._mqtt.reconnect_delay_set(min_delay=1, max_delay=120)
		##Retry the initial connect so a transient DNS/broker outage at startup
		##(e.g. "[Errno -2] Name or service not known", issue #73) does not abort
		##the whole daemon. Back off up to ~60s, then give up and re-raise.
		_attempt = 0
		while True:
			try:
				self._mqtt.connect(self.config["mqtt_host"], port=self.config["mqtt_port"], keepalive=60, bind_address="")
				break
			except (socket.gaierror, socket.timeout, ConnectionRefusedError, OSError) as e:
				_attempt += 1
				_wait = min(2 ** _attempt, 60)
				logger.warning("MQTT connect to %s:%s failed (%s); retry %s in %ss" % (self.config["mqtt_host"], self.config["mqtt_port"], e, _attempt, _wait))
				if _attempt >= 8:
					logger.error("MQTT connect giving up after %s attempts" % _attempt)
					raise
				time.sleep(_wait)
		
		
		##Start
		self._mqtt.loop_start()  # creates new thread and runs Mqtt.loop_forever() in it.
			
		

	def _on_mqtt_log(self,client, userdata, level, buf):
			
		if level == mqtt.MQTT_LOG_ERR:
			logger.debug("Mqtt log: " + buf)
		
	##*args absorbs the trailing `properties` paho appends under MQTTv5.
	def _mqtt_on_subscribe(self,client, userdata, mid, granted_qos, *args):
		logger.debug("Mqtt Subscribed")
		
	def _on_mqtt_message(self, client, userdata, msg):
		##paho tears down its network thread when a callback raises, which kills
		##every subscription and publish for the rest of the process life. Nothing
		##may escape from here.
		try:
			self._handle_mqtt_message(client, userdata, msg)
		except Exception as e:
			logger.error("Error handling message on %s: %s" % (msg.topic, e))
			logger.debug(traceback.format_exc())

	def _handle_mqtt_message(self, client, userdata, msg):
		##No try/except around the decode: a short topic or a non-ascii payload
		##lands in the guard above, which names the topic and logs a traceback.
		##The catch that used to be here reported the same failures as a bare
		##logger.critical(e) with no topic and no traceback, and swallowing them
		##first meant that richer handler could never see them.
		logger.debug('Mqtt Message Received! Userdata: %s, Message %s' % (userdata, msg.topic+" "+str(msg.payload)))
		##Function is second last .. decode to str #43
		function = str(msg.topic.split('/')[-2])
		address = msg.topic.split('/')[-3]
		##Make sure its proper STR .. python3  #43 .. very
		address = address.encode('ascii','ignore').decode("utf-8")
		#43 decode to force to str
		value = str(msg.payload.decode("ascii"))
		logger.debug('Mqtt decoded --> Function: %s, Address: %s, value: %s' %(function,address,value))

		##Devices that were skipped as unreachable, or commands arriving before
		##start() published the device map, have no object to talk to. Without this
		##every bare self.device_objects[address] below would raise.
		address = address.lower()
		if address not in self.device_objects:
			logger.warning("Ignoring '%s' command for unknown device %s" % (function, address))
			return

		##Process received		##Probably need to exit here as well if command not send, but should exit on status update above .. grr, hate stupid python
		if function ==  "temp":	
			try:
				if self.device_objects.get(address):
					status = self.device_objects[address].set_temperature(float(value))
					
					if status :
						self.publish_mqtt_info(status)
				else:
					logger.debug("Device not on list of devices %s, type:%s" % (address,type(address)))
					return
			except Exception as e:	
				logger.critical(e)
				return
			
		elif function == "power":
			if value.lower() == "on":
				status = self.device_objects[address].switch_on()
				if status :
					self.publish_mqtt_info(status)
			elif value.lower() == "off":
				status = self.device_objects[address].switch_off()
				if status :
					self.publish_mqtt_info(status)
			else:
				logger.debug("Switch has invalid value, values is on/off received %s",value)
				return
				
		elif function == "mode":
			
			status = self.device_objects[address].set_mode(value)
			if status :
				self.publish_mqtt_info(status)
				
			else:
				logger.debug("Mode has invalid value %s",value)
				return
	
		elif function == "fanspeed":
			if value.lower() == "turbo":
				status = self.device_objects[address].set_turbo("ON")
				
				#status = self.device_objects[address].set_mute("OFF")
			elif value.lower() == "mute":				
				status = self.device_objects[address].set_mute("ON")
				
			else:
				#status = self.device_objects[address].set_mute("ON")
				#status = self.device_objects[address].set_turbo("OFF")
				status = self.device_objects[address].set_fanspeed(value)

			if status :
				self.publish_mqtt_info(status)
				
			else:
				logger.debug("Fanspeed has invalid value %s",value)
				return
				
		elif function == "fanspeed_homeassistant":
			if value.lower() == "turbo":
				status = self.device_objects[address].set_turbo("ON")
				
				#status = self.device_objects[address].set_mute("OFF")
			elif value.lower() == "mute":				
				status = self.device_objects[address].set_mute("ON")
				
			else:
				#status = self.device_objects[address].set_mute("ON")
				#status = self.device_objects[address].set_turbo("OFF")
				status = self.device_objects[address].set_fanspeed(value)
			 
			if status :
				self.publish_mqtt_info(status)
				
			else:
				logger.debug("Fanspeed_homeassistant has invalid value %s",value)
				return
				
		elif function == "mode_homekit":
			
			status = self.device_objects[address].set_homekit_mode(value)
			if status :
				self.publish_mqtt_info(status)
				
			else:
				logger.debug("Mode_homekit has invalid value %s",value)
				return
		elif function == "mode_homeassistant":
			
			status = self.device_objects[address].set_homeassistant_mode(value)
			if status :
				self.publish_mqtt_info(status)
				
			else:
				logger.debug("Mode_homeassistant has invalid value %s",value)
				return		
		elif function == "state" :
			
			if value == "refresh":
				logger.debug("Refreshing states")
				status = self.device_objects[address].get_ac_status()
			else:
				logger.debug("Command not valid: "+ value)
				return

				
			if status:
				self.publish_mqtt_info(status,force_update=True)				
			else:
				logger.debug("Unable to refresh")
				return
			return
		elif function ==  "fixation_v":	
			try:
				if self.device_objects.get(address):
					status = self.device_objects[address].set_fixation_v(value)
					
					if status :
						self.publish_mqtt_info(status)
				else:
					logger.debug("Device not on list of devices %s, type:%s" % (address,type(address)))
					return
			except Exception as e:	
				logger.critical(e)
				return
		elif function ==  "fixation_h":	
			try:
				if self.device_objects.get(address):					
					status = self.device_objects[address].set_fixation_h(value)					
					if status :
						self.publish_mqtt_info(status)
				else:
					logger.debug("Device not on list of devices %s, type:%s" % (address,type(address)))
					return
			except Exception as e:	
				logger.critical(e)
				return
		elif function ==  "display":	
			try:
				if self.device_objects.get(address):					
					status = self.device_objects[address].set_display(value)					
					if status :
						self.publish_mqtt_info(status)
				else:
					logger.debug("Device not on list of devices %s, type:%s" % (address,type(address)))
					return
			except Exception as e:	
				logger.critical(e)
				return
		elif function ==  "mildew":	
			try:
				if self.device_objects.get(address):					
					status = self.device_objects[address].set_mildew(value)					
					if status :
						self.publish_mqtt_info(status)
				else:
					logger.debug("Device not on list of devices %s, type:%s" % (address,type(address)))
					return
			except Exception as e:	
				logger.critical(e)
				return
		elif function ==  "clean":	
			try:
				if self.device_objects.get(address):					
					status = self.device_objects[address].set_clean(value)					
					if status :
						self.publish_mqtt_info(status)
				else:
					logger.debug("Device not on list of devices %s, type:%s" % (address,type(address)))
					return
			except Exception as e:	
				logger.critical(e)
				return
		elif function ==  "health":	
			try:
				if self.device_objects.get(address):					
					status = self.device_objects[address].set_health(value)					
					if status :
						self.publish_mqtt_info(status)
				else:
					logger.debug("Device not on list of devices %s, type:%s" % (address,type(address)))
					return
			except Exception as e:	
				logger.critical(e)
				return
		elif function ==  "sleep":	
			try:
				if self.device_objects.get(address):					
					status = self.device_objects[address].set_sleep(value)					
					if status :
						self.publish_mqtt_info(status)
				else:
					logger.debug("Device not on list of devices %s, type:%s" % (address,type(address)))
					return
			except Exception as e:	
				logger.critical(e)
				return
		else:
			logger.debug("No function match")
			return
			
	def _on_mqtt_connect(self, client, userdata, flags, rc):

		"""
		RC definition:
		0: Connection successful
		1: Connection refused - incorrect protocol version
		2: Connection refused - invalid client identifier
		3: Connection refused - server unavailable
		4: Connection refused - bad username or password
		5: Connection refused - not authorised
		6-255: Currently unused.
		"""

		logger.debug('Mqtt connected! client=%s, userdata=%s, flags=%s, rc=%s' % (client, userdata, flags, rc))
		# Subscribing in on_connect() means that if we lose the connection and
		# reconnect then subscriptions will be renewed.
		sub_topic = self.config["mqtt_topic_prefix"]+ "+/+/set"
		client.subscribe(sub_topic)
		logger.debug('Listing on %s for messages' % (sub_topic))


		##LWT
		self._publish(self.config["mqtt_topic_prefix"]+'LWT','online',retain=True)

